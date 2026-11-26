"""get() must not mutate the caller's headers or share a default dict between calls."""

import unittest
from unittest import mock

from hardening_fixtures import fake_response, make_context

URL = "https://web.facebook.com/x"


class GetHeadersTest(unittest.TestCase):
    def test_caller_headers_not_mutated(self):
        ctx = make_context()
        headers = {"x-test": "1"}
        with mock.patch.object(ctx.session, "get", return_value=fake_response(ctx, URL)) as get:
            ctx.get(URL, headers=headers)
        self.assertEqual(headers, {"x-test": "1"})
        self.assertIn("accept", get.call_args.kwargs["headers"])

    def test_default_headers_not_shared(self):
        ctx = make_context()
        with mock.patch.object(ctx.session, "get", return_value=fake_response(ctx, URL)) as get:
            ctx.get(URL)
            get.call_args.kwargs["headers"]["x-leak"] = "1"
            ctx.get(URL)
        self.assertNotIn("x-leak", get.call_args.kwargs["headers"])


if __name__ == "__main__":
    unittest.main()
