pymacaron-unit
==============

Python library for unittesting json REST apis built with
[pymacaron](https://github.com/pymacaron/pymacaron), including support for JWT
authentication, Error formats used by pymacaron and compatible with
'run_acceptance_tests', the testing tool used in pymacaron microservices.

Synopsis
--------

.. code-block:: python

    from pymacaron_unit.testcase import PyMacaronTestCase

    class Tests(PyMacaronTestCase):

        def setUp(self):
            super.setUp()
            self.host = 'api.fixer.io'
            self.port = 80

        def test_make_some_calls(self):

            # Test that GET returns a json structure
            j = self.assertGetReturnJson(
                "v1/hello",
            )

            # Same, with setting the Authorization http header to a JWT token
            j = self.assertGetReturnJson(
                "v1/hello",
                auth="Bearer %s" % self.token
            )

            # Do a POST
            j = self.assertPostReturnJson(
                "v1/hello",
                {
                    'foo': 'bar',
                }
            )

See
[pymacaron_unit/testcase.py](https://github.com/pymacaron/pymacaron-unit/blob/master/pymacaron_unit/testcase.py)
for a complete list of test methods.


Examples
--------

See [test/test_unit.py](https://github.com/pymacaron/pymacaron-unit/blob/master/test/test_unit.py) :-)
