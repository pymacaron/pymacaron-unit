import os
from pymacaron_unit.testcase import PyMacaronTestCase

os.environ['PYM_SERVER_HOST'] = 'a.b.c.d'
os.environ['PYM_SERVER_PORT'] = '666'

class Tests(PyMacaronTestCase):

    def setUp(self):
        super().setUp()
        # Let's use the free currency exchange api at api.fixer.io for our tests
        self.host = 'data.fixer.io'
        self.port = 8080

    def test_get(self):
        j = self.assertGetReturnJson('api/latest?symbols=SEK&access_key=21f178a5294ea1508f8d8629e60a9ad4')
        self.assertTrue('SEK' in j['rates'])
