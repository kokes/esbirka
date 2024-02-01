import io
from urllib.request import urlopen
from zipfile import ZipFile

OPENAPI_URL = (
    "https://opendata.eselpoint.cz/dokumentace/Definicni_soubor_REST_API_e-Sbirka.zip"
)


if __name__ == "__main__":
    with urlopen(OPENAPI_URL) as r:
        data = io.BytesIO(r.read())
        with ZipFile(data) as zf:
            files = [j.filename for j in zf.filelist]
            assert files == ["daver.json"]
            zf.extract("daver.json", ".")
