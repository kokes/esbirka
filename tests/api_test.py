import threading
import json
from urllib.request import urlopen
from unittest import TestCase
from http.server import HTTPServer

from api import API


class TestAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        # Start a test server in a separate thread
        cls.server = HTTPServer(("localhost", 8001), API)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def build_url(self, path: str) -> str:
        assert path.startswith("/"), path
        return f"http://{self.server.server_address[0]}:{self.server.server_port}{path}"

    # TODO: parametrise this
    def test_sbirky(self):
        url = self.build_url("/sbirky")
        with open("tests/responses/sbirky.json") as f:
            expected = json.load(f)

        with urlopen(url) as f:
            data = json.load(f)

        self.assertEqual(data, expected)
