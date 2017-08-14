import os
from klue_unit.testcase import KlueTestCase

os.environ['KLUE_SERVER_HOST'] = 'a.b.c.d'
os.environ['KLUE_SERVER_PORT'] = '666'

class Tests(KlueTestCase):

    def setUp(self):
        super().setUp()
        # Let's use the free currency exchange api at api.fixer.io for our tests
        self.host = 'api.fixer.io'
        self.port = 80

    def test_get(self):
        j = self.assertGetReturnJson('latest?symbols=SEK')
        self.assertTrue('SEK' in j['rates'])
