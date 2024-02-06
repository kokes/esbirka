import csv
import gzip
import os
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
    Dataset(
        "013CiselnikTypFragmentu.csv.gz",
        "ciselnik_typ_fragmentu",
        {  # TODO: vsechny ciselniky maj stejnej mapping (byt tady neni zkratka)
            "id-esb": ("id", int),
            "kód": ("kod", str),
            "název": ("nazev", str),
        },
    ),
]


@dataclass
class Endpoint:
    method: str
    path: str
    query: str


endpoints = [
    Endpoint(
        "GET", "/sbirky", "SELECT zkratka, nazev, kod FROM ciselnik_sbirka ORDER BY id"
    ),
    Endpoint(
        "GET",
        "/typ-fragmentu",
        "SELECT nazev, kod FROM ciselnik_typ_fragmentu ORDER BY kod COLLATE NOCASE",
    ),
]

endpointmap = {e.path: e for e in endpoints}


class API(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.conn = sqlite3.connect("api.db")  # TODO: pass this in
        super().__init__(*args, **kwargs)

    def do_GET(self):
        ep = endpointmap.get(self.path)
        if not ep:
            self.send_response(404)
            self.end_headers()
            return

        c = self.conn.execute(ep.query)
        rows = []
        header = [d[0] for d in c.description]
        for row in c:
            rows.append(dict(zip(header, row)))
        data = json.dumps({"seznam": rows}, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(data))
        self.send_header("Content-Encoding", "utf-8")
        self.end_headers()
        self.wfile.write(data)


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

    print("Database created.")
    for endpoint in endpoints:
        print(f"{endpoint.method} {endpoint.path} {endpoint.query}")
    print(f"Found {len(endpoints)} endpoints.")

    print("Listening on http://localhost:8000")
    httpd = ThreadingHTTPServer(("localhost", 8000), API)
    httpd.serve_forever()
