import os
from klue_unit.testcase import KlueTestCase

os.environ['KLUE_SERVER_HOST'] = 'a.b.c.d'
os.environ['KLUE_SERVER_PORT'] = '666'

class Tests(KlueTestCase):

    def test_loads(self):
        pass

    def test_load_port_host_token(self):
        tests = [
            # KLUE_SERVER_HOST, KLUE_SERVER_PORT, KLUE_JWT_TOKEN, expected host, port, token
            ['1.2.3.4', '8080', None, '1.2.3.4', '8080', None],
        ]

        for env_host, env_port, env_token, want_host, want_port, want_token in tests:
            os.environ['KLUE_SERVER_HOST'] = env_host
            os.environ['KLUE_SERVER_PORT'] = env_port
            if env_token:
                os.environ['KLUE_JWT_TOKEN'] = env_token

            self.setUp()

            self.assertEqual(self.host, want_host)
            self.assertEqual(self.port, want_port)
            self.assertEqual(self.token, want_token)
