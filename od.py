import sys
import io
import json
from typing import Iterator

LIST_START = '"položky":['
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


if __name__ == "__main__":
    fn = sys.argv[1]

    with open(fn, "rt") as f:
        for item in get_items(f):
            pass
