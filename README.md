klue-unit
=========

Python library for unittesting json REST apis, with support for Authorization
header and Error formats used by klue-client-server.

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

See klue_unit/testcase.py for a complete list of test methods. Bear in mind
that most of them are customized for use against apis implemented with
klue-client-server.


Examples
--------

See test/test_klue_unit.py :-)