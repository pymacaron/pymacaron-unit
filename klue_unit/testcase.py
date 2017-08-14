import os
import json
import re
import requests
import urllib.request
import urllib.error
import urllib.parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import ReadTimeout
import unittest
import logging
import pprint
from klue.swagger.apipool import ApiPool


log = logging.getLogger(__name__)


def load_port_host_token():
    """Find out which host:port to run acceptance tests against,
    using the environment variables KLUE_SERVER_HOST, KLUE_SERVER_PORT
    """

    server_host, server_port, token = (None, None, None)

    if 'KLUE_SERVER_HOST' in os.environ:
        server_host = os.environ['KLUE_SERVER_HOST']
    if 'KLUE_SERVER_PORT' in os.environ:
        server_port = os.environ['KLUE_SERVER_PORT']

    token = os.environ.get('KLUE_JWT_TOKEN', None)

    if server_host:
        if server_host.startswith('http://'):
            server_host = server_host[7:]
        if server_host.startswith('https://'):
            server_host = server_host[8:]
        if server_host.endswith('/'):
            server_host = server_host[:-1]

    if not server_host or not server_port:
        raise Exception("Please set both of KLUE_SERVER_HOST and KLUE_SERVER_PORT envvironment variables")

    return (server_host, server_port, token)

#
# PntTest testcase object
#

class KlueTestCase(unittest.TestCase):

    host = None
    port = None
    token = None
    timeout_connect = 10
    timeout_read = 10

    def setUp(self):
        self.maxDiff = None
        self.host, self.port, self.token = load_port_host_token()

    def cleanup(self):
        raise Exception("Not implemented! Please override cleanup() in the child class.")

    def load_client(self, name, **kwargs):

        log.info("Loading client api for %s" % name)

        def get_path(f):
            return os.path.join(
                os.path.realpath(os.path.dirname(__file__)),
                '..',
                'apis',
                f
            )

        name_to_yaml = {
            'klue': get_path('klue-api.yaml'),
            'login': get_path('login.yaml'),
            'seller': get_path('seller.yaml'),
            'item': get_path('item.yaml'),
            'expert': get_path('expert-api.yaml'),
            'cert': get_path('cert.yaml'),
            'announce': get_path('announce.yaml'),
            'search': get_path('search-api.yaml'),
            'chatbot': get_path('chatbot.yaml'),
            'market': get_path('market.yaml'),
        }

        if name not in name_to_yaml:
            raise Exception("Don't know service %s" % name)

        # Override https in yaml file if testing a port 80/8080
        if 'port' in kwargs and kwargs['port'] and int(kwargs['port']) in (80, 8080):
            kwargs['proto'] = 'http'

        if 'NO_SSL_CHECK' in os.environ:
            if os.environ.get('NO_SSL_CHECK') != '':
                kwargs['verify_ssl'] = False
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        ApiPool.add(
            name,
            yaml_path=name_to_yaml[name],
            formats=get_custom_formats(),
            **kwargs
        )

    def _try(self, method, url, headers, data, allow_redirects=True, verify_ssl=True):

        my_verify_ssl = verify_ssl
        if 'NO_SSL_CHECK' in os.environ:
            if os.environ.get('NO_SSL_CHECK') != '':
                my_verify_ssl = False

        if not my_verify_ssl:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Try up to 3 times if we get a ReadTimeout and request has no data
        if data is None:
            jdata = None
        elif type(data) is dict:
            jdata = json.dumps(data)
            headers['Content-Type'] = 'application/json'
        elif type(data) is str:
            jdata = data
        else:
            raise Exception("Unsupported data type %s" % data)

        if jdata:
            log.debug("POSTING DATA: %s" % jdata)

        last_exception = None
        for i in range(3):
            try:
                log.info("Calling %s %s" % (method, url))
                f = getattr(requests, method)
                r = f(
                    url,
                    headers=headers,
                    data=jdata,
                    timeout=(5 * timeout_connect, 5 * timeout_read),
                    verify=my_verify_ssl,
                    allow_redirects=allow_redirects,
                )
                return r
            except Exception as e:

                last_exception = e

                if isinstance(e, ReadTimeout):
                    log.warn("Got a ReadTimeout calling %s %s" % (method, url))
                    log.warn("Exception was: %s" % str(e))

                    retry = False

                    resp = e.response
                    if not resp:
                        log.info("Requests error has no response.")
                        # retry = True   # TODO: once I am sure we can retry, set to True
                    else:
                        b = resp.content
                        log.info("Requests has a response with content: " + pprint.pformat(b))
                        log.info("Not Retrying.")

                    if method == 'get':
                        log.warn("Query was a GET: let's retry!")
                        retry = True

                    if retry:
                        continue

                raise e

        raise last_exception

    def _assertMethodReturnContent(self, path, method, data, status, auth, contenttype, allow_redirects=True, verify_ssl=True, port=None, quiet=False):
        method = method.lower()
        assert method in ('post', 'get', 'delete', 'patch', 'put')
        assert self.host and self.port, "self.host|port undefined. Did you call setUp()?"

        self.assertTrue(type(path) is str, "[%s] is str/unicode (type: %s)" % (path, str(type(path))))
        self.assertTrue(isinstance(status, int), "[%s] is int" % status)

        target_port = self.port
        if port:
            target_port = port
        protocol = 'https' if target_port == '443' else 'http'
        path = path.lstrip('/')
        url = "%s://%s:%s/%s" % (protocol, self.host, target_port, path)
        headers = {}
        if contenttype:
            headers['Content-Type'] = contenttype
        if auth:
            headers['Authorization'] = auth
        print("calling %s %s" % (method.upper(), url))
        r = self._try(method, url, headers, data, allow_redirects=allow_redirects, verify_ssl=verify_ssl)
        if not quiet:
            print("r: %s" % r.text)
        self.assertEqual(r.status_code, status)
        return r

    def _assertMethodReturnJson(self, path, method, data, status, auth, verify_ssl=True):
        r = self._assertMethodReturnContent(path, method, data, status, auth, 'application/json', verify_ssl=verify_ssl)
        j = r.json()
        return j

    def _assertMethodReturnDict(self, path, method, data, kv, status, auth, verify_ssl=True):
        self.assertTrue(isinstance(kv, dict), "[%s] is dict" % kv)
        assert isinstance(kv, dict)
        j = self._assertMethodReturnJson(path, method, data, status, auth, verify_ssl=verify_ssl)
        for k, v in kv.items():
            self.assertTrue(k in j, "%s in json %s" % (k, json.dumps(j)))
            self.assertEqual(j[k], v)
        return j

    #
    # Test calling an endpoint returns the right json/status
    #

    def assertGetReturnJson(self, path, status=200, auth=None, verify_ssl=True):
        return self._assertMethodReturnJson(path, 'get', None, status, auth, verify_ssl=verify_ssl)

    def assertDeleteReturnJson(self, path, status=200, auth=None):
        return self._assertMethodReturnJson(path, 'delete', None, status, auth)

    def assertPostReturnJson(self, path, data, status=200, auth=None, verify_ssl=True):
        return self._assertMethodReturnJson(path, 'post', data, status, auth, verify_ssl=verify_ssl)

    def assertGetReturnDict(self, path, kv, status=200, auth=None, verify_ssl=True):
        return self._assertMethodReturnDict(path, 'get', None, kv, status, auth, verify_ssl=verify_ssl)

    def assertPostReturnDict(self, path, data, kv, status=200, auth=None, verify_ssl=True):
        return self._assertMethodReturnDict(path, 'post', data, kv, status, auth, verify_ssl=verify_ssl)

    def assertGetReturnOk(self, path, auth=None):
        j = self.assertGetReturnJson(path, 200, auth)
        return self.assertDictEqual(j, {})

    def assertPostReturnOk(self, path, data, auth=None):
        j = self.assertPostReturnJson(path, data, 200, auth)
        return self.assertDictEqual(j, {})

    def assertGetReturnError(self, path, status, error, auth=None, verify_ssl=True):
        self.assertTrue(isinstance(error, str), "[%s] is str" % error)
        return self.assertGetReturnDict(path, {'status': status, 'error': error}, status, auth, verify_ssl=verify_ssl)

    def assertPostReturnError(self, path, data, status, error, auth=None, verify_ssl=True):
        self.assertTrue(isinstance(error, str), "[%s] is str" % error)
        return self.assertPostReturnDict(path, data, {'status': status, 'error': error}, status, auth, verify_ssl=verify_ssl)

    # More generic calls
    def assertCallReturnJson(self, method, path, data=None, auth=None, status=200):
        return self._assertMethodReturnJson(path, method, data, status, auth)

    def assertCallReturnDict(self, method, path, kv, data=None, auth=None, status=200):
        return self._assertMethodReturnDict(path, method, data, kv, status, auth)

    def assertCallReturnOk(self, method, path, data=None, auth=None):
        j = self.assertCallReturnJson(method, path, data, auth, 200)
        return self.assertDictEqual(j, {})

    def assertCallReturnError(self, method, path, status, error, data=None, auth=None):
        self.assertTrue(isinstance(error, str), "[%s] is str" % error)
        return self.assertCallReturnDict(
            method,
            path,
            {'status': status, 'error': error},
            data,
            auth,
            status
        )

    def assertCallReturnHtml(self, method, path, data=None, auth=None, status=200, allow_redirects=True, verify_ssl=True, quiet=False):
        r = self._assertMethodReturnContent(path, method, data, status, auth, None, allow_redirects=allow_redirects, verify_ssl=verify_ssl, quiet=quiet)
        self.assertEqual(r.headers['Content-Type'], 'text/html; charset=utf-8')
        return r.text

    def assertCallReturnText(self, method, path, data=None, auth=None, status=200, allow_redirects=True, verify_ssl=True, quiet=False):
        r = self._assertMethodReturnContent(path, method, data, status, auth, None, allow_redirects=allow_redirects, verify_ssl=verify_ssl, quiet=quiet)
        self.assertEqual(r.headers['Content-Type'], 'text/plain; charset=utf-8')
        return r.text


    #
    # Test for default endpoints: /ping /version /secured/version
    #

    def assertHasPing(self):
        self.assertGetReturnOk('ping')

    def assertHasVersion(self, verify_ssl=True):
        j = self.assertGetReturnJson('version', 200, verify_ssl=verify_ssl)
        self.assertIsVersion(j)

    def assertHasAuthVersion(self, verify_ssl=True):
        self.assertGetReturnError('secured/version', 401, 'AUTHORIZATION_HEADER_MISSING', verify_ssl=verify_ssl)

        tests = [
            # header,  status code, json code
            ("", 401, 'AUTHORIZATION_HEADER_MISSING'),
            ("Bearer1234567890", 401, 'TOKEN_INVALID'),
            ("bearer foo bar", 401, 'TOKEN_INVALID'),
            ("Bearer 1234567890", 401, 'TOKEN_INVALID'),
        ]

        for t in tests:
            token, status, error = t
            self.assertGetReturnError('secured/version', status, error, token, verify_ssl=verify_ssl)

        j = self.assertGetReturnJson('secured/version', 200, "Bearer %s" % self.token, verify_ssl=verify_ssl)
        self.assertIsVersion(j)
