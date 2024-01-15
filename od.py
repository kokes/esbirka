import argparse
import csv
import gzip
import io
import json
import logging
import multiprocessing as mp
import os
import re
import ssl
from functools import partial
from glob import glob
from itertools import islice
from typing import Iterator
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://opendata.eselpoint.cz/datove-sady-esbirka/"
OUTDIR = "data"
SRC_SUFFIX = ".jsonld.gz"

LIST_START = '"položky":['
LIST_EMPTY = "[]"

ITEM_START = "{\n"
ITEM_CONT = "},\n"
ITEM_LAST = "}\n"
ITEM_END = (ITEM_CONT, ITEM_LAST)


def get_items(r: io.TextIOBase) -> Iterator[dict]:
    found_list = False
    in_item = False
    item_lines = []
    for line in r:
        if not found_list:
            if line.startswith(LIST_START):
                found_list = True
                if LIST_EMPTY in line:
                    return
            continue

        if not in_item:
            assert line == ITEM_START, line
            in_item = True

        item_lines.append(line)

        if in_item and line in ITEM_END:
            in_item = False
            raw = ("".join(item_lines)).rstrip(",\n")
            item = json.loads(raw)
            yield item
            item_lines = []
            if line == ITEM_LAST:
                return

    if not found_list:
        raise ValueError("List not found")


def convert_from_url(url: str, fmt: str, partial: bool) -> tuple[str, int]:
    records = 0
    filename = os.path.basename(urlparse(url).path)
    if fmt == "csv":
        filename = filename.replace(SRC_SUFFIX, ".csv.gz")
    outfile = os.path.join(OUTDIR, filename)
    if os.path.exists(outfile):
        return filename, -1

    outfile_tmp = outfile + ".tmp"

    url_full = urljoin(BASE_URL, url)
    logging.info("Downloading %s", url_full)

    with (
        urlopen(url_full) as r,
        gzip.open(r, "rt") as f,
        gzip.open(outfile_tmp, "wt") as fw,
    ):
        # classification files are messed up, their format is different
        if "ciselnik" in filename.lower():
            items = json.load(f)["položky"]
        else:
            items = get_items(f)

        if partial:
            items = islice(items, 1000)

        if fmt == "csv":
            cw = csv.writer(fw)
            header = None
            logged_obj = set()

        for item in items:
            records += 1
            if fmt == "json":
                json.dump(item, fw, ensure_ascii=False)
                fw.write("\n")
            elif fmt == "csv":
                if header is None:
                    header = list(item.keys())
                    cw.writerow(header)
                row = [item.get(h, "") for h in header]
                cw.writerow(row)

                # mame objektovy sloupec?
                if objy := [
                    k for k, v in zip(header, row) if isinstance(v, (list, dict))
                ]:
                    for k in objy:
                        if (filename, k) not in logged_obj:
                            logged_obj.add((filename, k))
                            val = json.dumps(row[header.index(k)], ensure_ascii=False)[
                                :500
                            ]
                            logging.warning(
                                "object-like column: %s: %s (%s)", filename, k, val
                            )

    os.rename(outfile_tmp, outfile)
    return filename, records


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--partial", action="store_true")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    args = parser.parse_args()

    with urlopen(BASE_URL) as r:
        dt = r.read().decode("utf-8")

    urls = re.findall(r"href=['\"](.+?\.gz)['\"]", dt)
    assert len(urls) > 0
    urls_json = [url for url in urls if url.endswith(".json.gz")]
    urls_jsonld = [url for url in urls if url.endswith(SRC_SUFFIX)]
    assert len(urls_json) == len(urls_jsonld)
    assert len(urls_jsonld) > 0

    os.makedirs(OUTDIR, exist_ok=True)
    for file in glob(os.path.join(OUTDIR, "*.tmp")):
        os.remove(file)

    ncpu = mp.cpu_count()
    processor = partial(convert_from_url, fmt=args.format, partial=args.partial)
    with mp.Pool(ncpu) as pool:
        for filename, records in pool.imap_unordered(processor, urls_jsonld):
            logging.info("%s: %d records", filename, records)
