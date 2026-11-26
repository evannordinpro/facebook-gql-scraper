"""Offline fixtures for the hardening tests: no request reaches Facebook."""

import json
import os
import tempfile

import requests

import facebook_gql_scraper as fgs

SECRET = "SECRET-SESSION-VALUE"


def make_context(**kwargs) -> fgs.FacebookContext:
    tmp = tempfile.mkdtemp()
    cookies_file = os.path.join(tmp, "cookies.json")
    with open(cookies_file, "w", encoding="utf-8") as f:
        json.dump([{"name": "c_user", "value": "1"}, {"name": "xs", "value": SECRET}], f)
    kwargs.setdefault("state_file", os.path.join(tmp, "state.json"))
    kwargs.setdefault("debug_dir", os.path.join(tmp, "debug"))
    return fgs.FacebookContext(cookies_file=cookies_file, quiet=True, **kwargs)


def fake_response(ctx: fgs.FacebookContext, url: str) -> requests.Response:
    prepared = ctx.session.prepare_request(requests.Request("GET", url))
    response = requests.Response()
    response.status_code = 200
    response.reason = "OK"
    response.url = url
    response.request = prepared
    response._content = b"<html></html>"
    return response
