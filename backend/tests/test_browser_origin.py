"""Regression tests for the browser origin policy."""

import pytest

from app.browser_origin import permits_browser_request

TRUSTED_ORIGIN = "http://127.0.0.1:8000"


@pytest.mark.parametrize(
    ("method", "origins", "expected"),
    [
        ("GET", [], True),
        ("HEAD", [], True),
        ("OPTIONS", [], True),
        ("GET", ["https://evil.example"], False),
        ("POST", [TRUSTED_ORIGIN], True),
        ("PUT", [TRUSTED_ORIGIN], True),
        ("DELETE", [], False),
        ("POST", ["null"], False),
        ("POST", ["https://evil.example"], False),
        ("POST", [TRUSTED_ORIGIN + ".evil.example"], False),
        ("POST", [TRUSTED_ORIGIN, TRUSTED_ORIGIN], False),
        ("POST", [TRUSTED_ORIGIN + ", https://evil.example"], False),
        ("POST", ["http://localhost:8000"], False),
        ("CUSTOM", [], False),
    ],
)
def test_browser_origin_policy(method, origins, expected):
    assert permits_browser_request(method, origins, TRUSTED_ORIGIN) is expected


@pytest.mark.parametrize("trusted_origin", ["", "null"])
def test_missing_configuration_fails_closed(trusted_origin):
    assert not permits_browser_request("GET", [], trusted_origin)
    assert not permits_browser_request("POST", [trusted_origin], trusted_origin)
