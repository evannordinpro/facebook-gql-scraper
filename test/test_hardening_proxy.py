"""Setting a proxy must not silently turn off TLS certificate checks."""

import unittest

from hardening_fixtures import make_context


class ProxyTlsTest(unittest.TestCase):
    def test_proxy_keeps_tls_verification(self):
        ctx = make_context(proxy="http://127.0.0.1:8080")
        self.assertEqual(ctx.session.proxies["https"], "http://127.0.0.1:8080")
        self.assertIs(ctx.session.verify, True)


if __name__ == "__main__":
    unittest.main()
