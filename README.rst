klue-unit
=========

Python library for unittesting json REST apis built with
[klue-microservice](https://github.com/erwan-lemonnier/klue-microservice),
including support for JWT authentication, Error formats used by
klue-microservice and compatible with 'run_acceptance_tests', the testing tool
used in klue microservices.

Synopsis
--------

.. code-block:: python

    from klue_unit.testcase import KlueTestCase

    class Tests(KlueTestCase):

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
[klue_unit/testcase.py](https://github.com/erwan-lemonnier/klue-unit/blob/master/klue_unit/testcase.py)
for a complete list of test methods.


Examples
--------

See [test/test_klue_unit.py](https://github.com/erwan-lemonnier/klue-unit/blob/master/test/test_klue_unit.py) :-)