import gzip
import io
import json
import os
from glob import glob
from typing import Iterator

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


if __name__ == "__main__":
    files = glob("data/*.jsonld.gz")
    outdir = "out/"
    os.makedirs(outdir, exist_ok=True)

    for file in glob(os.path.join(outdir, "*.tmp")):
        os.remove(file)

    for file in files:
        outfile = os.path.join(outdir, os.path.basename(file))
        if os.path.exists(outfile):
            continue
        outfile_tmp = outfile + ".tmp"

        print(file)
        with gzip.open(file, "rt") as f, gzip.open(outfile_tmp, "wt") as fw:
            # classification files are messed up, their format is different
            if "ciselnik" in file.lower():
                items = json.load(f)["položky"]
            else:
                items = get_items(f)

            for item in items:
                json.dump(item, fw, ensure_ascii=False)
                fw.write("\n")

        os.rename(outfile_tmp, outfile)
