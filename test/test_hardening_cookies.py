"""Session cookies must never reach a host other than Facebook."""

import unittest
from unittest import mock

import requests

from hardening_fixtures import SECRET, fake_response, make_context


class CookieScopeTest(unittest.TestCase):
    def test_cookies_sent_to_facebook(self):
        ctx = make_context()
        req = ctx.session.prepare_request(requests.Request("GET", "https://web.facebook.com/"))
        self.assertIn(SECRET, req.headers.get("Cookie", ""))

    def test_cookies_not_sent_to_other_hosts(self):
        ctx = make_context()
        req = ctx.session.prepare_request(requests.Request("GET", "https://example.com/"))
        self.assertNotIn(SECRET, req.headers.get("Cookie", ""))

    def test_get_refuses_non_facebook_hosts(self):
        ctx = make_context()
        with mock.patch.object(ctx.session, "get") as get:
            with self.assertRaises(ValueError):
                ctx.get("https://example.com/script.js")
            get.assert_not_called()

    def test_get_allows_facebook_and_its_cdn(self):
        ctx = make_context()
        for url in ("https://web.facebook.com/x", "https://static.xx.fbcdn.net/rsrc.php/a.js"):
            with mock.patch.object(ctx.session, "get", return_value=fake_response(ctx, url)):
                ctx.get(url)

    def test_get_refuses_lookalike_hosts(self):
        ctx = make_context()
        with mock.patch.object(ctx.session, "get") as get:
            for url in ("https://facebook.com.evil.io/", "https://notfacebook.com/", "http://web.facebook.com/"):
                with self.assertRaises(ValueError, msg=url):
                    ctx.get(url)
            get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
