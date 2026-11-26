"""Debug dumps must not write session cookies or CSRF tokens to disk."""

import os
import unittest

import requests

from hardening_fixtures import SECRET, fake_response, make_context

TOKEN = "DTSG-TOKEN-VALUE"


def _dumped(debug_dir: str) -> str:
    text = ""
    for root, _, files in os.walk(debug_dir):
        for name in files:
            with open(os.path.join(root, name), encoding="utf-8") as f:
                text += f.read()
    return text


class DebugRedactionTest(unittest.TestCase):
    def test_get_dump_redacts_cookies(self):
        ctx = make_context(debug=True)
        response = fake_response(ctx, "https://web.facebook.com/groups/1")
        self.assertIn(SECRET, response.request.headers["Cookie"])
        ctx.debug_response(response)
        dumped = _dumped(ctx.debug_dir)
        self.assertTrue(dumped)
        self.assertNotIn(SECRET, dumped)

    def test_post_dump_redacts_cookies_and_tokens(self):
        ctx = make_context(debug=True)
        body = f"av=1&fb_dtsg={TOKEN}&lsd={TOKEN}&variables=%7B%7D"
        prepared = ctx.session.prepare_request(
            requests.Request("POST", "https://web.facebook.com/api/graphql/", data=body)
        )
        response = fake_response(ctx, "https://web.facebook.com/api/graphql/")
        response.request = prepared
        response._content = b'{"data": {}}'
        ctx.debug_response(response, operation_name="Op", doc_id="1")
        dumped = _dumped(ctx.debug_dir)
        self.assertIn("fb_dtsg", dumped)
        self.assertNotIn(SECRET, dumped)
        self.assertNotIn(TOKEN, dumped)


if __name__ == "__main__":
    unittest.main()
