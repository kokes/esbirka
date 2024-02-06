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

    def test_endpoint(self):
        # TODO: refreshni ty snapshoty nejak poloautomaticky
        tests = [
            ("/sbirky", "tests/responses/sbirky.json"),
            ("/typ-fragmentu", "tests/responses/typ-fragmentu.json"),
        ]

        for path, expected_fn in tests:
            with self.subTest(path=path):
                url = self.build_url(path)
                with open(expected_fn) as f:
                    expected = json.load(f)

                with urlopen(url) as f:
                    data = json.load(f)

                self.assertEqual(data, expected)


# GET /czechvoc-schemata-konceptu []
# GET /czechvoc-stavy-konceptu []
# GET /czechvoc-typy-definic-terminu []
# GET /czechvoc-typy-poznamek []
# GET /czechvoc-typy-vazeb-souvisejici-termin []
# GET /podtypyaktu []
# GET /typy-aktu []
# GET /typy-dokumentu []
# POST /czechvoc-jednoducha-vyhledavani []
# POST /czechvoc-koncepty/asociace/dokumenty-sbirky []
# POST /czechvoc-koncepty/vyskyty/dokumenty-sbirky []
# POST /czechvoc-koncepty/vyskyty/zneni []
# GET /czechvoc-pravni-oblasti []
# POST /czechvoc-rozsirena-vyhledavani []
# POST /chronologicke-rejstriky/roky []
# POST /chronologicke-rejstriky/dokumenty-sbirky-po-mesicich []
# POST /chronologicke-rejstriky/castky-po-mesicich []
# GET /sady-dokumentu []
# POST /jednoducha-vyhledavani []
# POST /jednoducha-vyhledavani/zneni []
# POST /rozsirena-vyhledavani []
# POST /rozsirena-vyhledavani/zneni []
# GET /castky/{kodSbirky}/{rok}/{cislo} []
# GET /castky/{kodSbirky}/{rok}/{cislo}/opravy []
# GET /czechvoc-jednoducha-vyhledavani/nabidka ['text', 'maxPocet']
# GET /czechvoc-koncepty/{kodSchematuKonceptu}/{klic} []
# POST /czechvoc-rejstriky/{kodSchematuKonceptu} []
# POST /czechvoc-rejstriky/{kodSchematuKonceptu}/{nadrazenyKonceptKlic} []
# GET /dokumenty-sbirky/{staleUrl} ['odkazId']
# GET /dokumenty-sbirky/{staleUrl}/citizen-summary []
# GET /dokumenty-sbirky/{staleUrl}/duvodove-zpravy []
# GET /dokumenty-sbirky/{staleUrl}/historie []
# GET /dokumenty-sbirky/{staleUrl}/dalsi-informace []
# GET /dokumenty-sbirky/{staleUrl}/zrusujici-nalezy-ustavniho-soudu []
# GET /dokumenty-sbirky/{staleUrl}/fragmenty/{fragmentId}/novelizace-a-derogace []
# GET /dokumenty-sbirky/{staleUrl}/souvislosti []
# GET /dokumenty-sbirky/{staleUrl}/fragmenty/{fragmentId}/ostatni-kontextove-informace []
# GET /dokumenty-sbirky/{staleUrl}/souvislosti/{typSouvislosti}/{souvisejiciStaleUrl} []
# GET /dokumenty-sbirky/{staleUrl}/odkazy-ke-stazeni []
# GET /dokumenty-sbirky/{staleUrl}/vykladova-stanoviska ['fulltextJednoZeSlov', 'fulltextVsechnaSlova', 'fulltextUvedenaFraze']
# GET /dokumenty-sbirky/{staleUrl}/fragmenty/{fragmentId}/vykladova-stanoviska []
# GET /dokumenty-sbirky/zmeny-zneni ['datumCasOdberuOd', 'razeni', 'start', 'pocet']
# GET /dokumenty-sbirky/depublikovana-zneni ['datumCasOdberuOd', 'razeni', 'start', 'pocet']
# GET /dokumenty-sbirky/{staleUrl}/nabidka-ustanoveni ['text', 'maxPocet']
# GET /dokumenty-sbirky/{staleUrl}/fragmenty ['cisloStranky', 'fulltextJednoZeSlov', 'fulltextVsechnaSlova', 'fulltextUvedenaFraze']
# GET /dokumenty-sbirky/{staleUrl}/citizen-summary/fragmenty ['cisloStranky', 'fulltextJednoZeSlov', 'fulltextVsechnaSlova', 'fulltextUvedenaFraze']
# GET /dokumenty-sbirky/{staleUrl}/duvodova-zprava/fragmenty ['cisloStranky', 'fulltextJednoZeSlov', 'fulltextVsechnaSlova', 'fulltextUvedenaFraze']
# GET /dokumenty-sbirky/{staleUrl}/souvisejici-dokumenty/{souvisejiciDokumentId}/fragmenty ['cisloStranky']
# GET /dokumenty-sbirky/{staleUrl}/id []
# GET /dokumenty-sbirky/{staleUrl}/fragmenty/{fragmentId}/konsolidacni-konflikty []
# GET /dokumenty-sbirky/{staleUrl}/fragmenty/{fragmentId}/upozorneni []
# GET /souborove-dokumenty/{id}/{druhObsahu}/{operace}/{nazevSouboru} []
# GET /stahni/overene-zneni/{dokumentId} []
# GET /stahni/pravne-zavazne-zneni/{dokumentId}/{formatSouboru} []
# GET /stahni/uplne-zneni-editoru-elegislativy/{dokumentId} []
# GET /stahni/pravne-zavazne-uplna-zneni/{dokumentId}/{metadataDokumentuId} []
# GET /stahni/pravne-zavazne-zneni-vcetne-uplnych/{dokumentId} []
# GET /stahni/souvisejici-dokumenty/{dokumentId}/{formatSouboru}/{typDokumentu} []
# GET /rejstriky/{typRejstriku} ['razeni', 'start', 'pocet']
# GET /jednoducha-vyhledavani/nabidka ['text', 'maxPocet']
# GET /rozsirena-vyhledavani/nabidka-nazvu-dokumentu-sbirky ['castNazvu', 'maxPocet']
# GET /rozsirena-vyhledavani/nabidka-kodu-dokumentu-sbirky ['castCisla', 'maxPocet']
# GET /rozsirena-vyhledavani/{kodSchematuKonceptu}/nabidka-nazvu-konceptu-czechvoc ['castNazvu', 'maxPocet']
# GET /rozsirena-vyhledavani/nabidka-kodu-castek ['castKodu', 'maxPocet']
