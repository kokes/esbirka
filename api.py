import csv
import gzip
import os
import json
import sqlite3
from dataclasses import dataclass

DATA_DIR = "data"


@dataclass
class Dataset:
    filename: str
    table_name: str
    conv: dict


typemap = {
    int: "INTEGER",
    str: "TEXT",
}
datasets = [
    Dataset(
        "012CiselnikSbirka.csv.gz",
        "ciselnik_sbirka",
        {
            "id-esb": ("id", int),  # TODO: proper dataclass here - incl. pkey, nullable
            "kód": ("kod", str),
            "zkratka": ("zkratka", str),
            "název": ("nazev", str),
        },
    ),
]

if __name__ == "__main__":
    conn = sqlite3.connect("api.db")
    with conn:
        c = conn.cursor()
        for dataset in datasets:
            with gzip.open(os.path.join(DATA_DIR, dataset.filename), "rt") as f:
                c.execute(f"DROP TABLE IF EXISTS {dataset.table_name}")
                reader = csv.DictReader(f)  # TODO: validate header?
                cols = ", ".join(
                    [
                        f"{v} {typemap[t]} NOT NULL"
                        for (k, (v, t)) in dataset.conv.items()
                    ]
                )
                schema = f"CREATE TABLE IF NOT EXISTS {dataset.table_name} ({cols})"
                c.execute(schema)
                for row in reader:
                    row = {
                        dataset.conv[k][0]: v
                        for k, v in row.items()
                        if k in dataset.conv
                    }
                    for k, v in row.items():
                        if v.startswith("{"):
                            val = json.loads(v)
                            assert val.keys() == {"cs"}, val
                            row[k] = val["cs"]

                    keys = ", ".join(row.keys())
                    values = ", ".join("?" * len(row))
                    c.execute(
                        f"INSERT INTO {dataset.table_name} ({keys}) VALUES ({values})",
                        list(row.values()),
                    )
