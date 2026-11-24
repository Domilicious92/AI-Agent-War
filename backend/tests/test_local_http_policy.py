"""Regression tests for the server-owned HTTP trust boundary."""

import pytest

from app.local_http_policy import LocalHttpPolicy


@pytest.mark.parametrize("host", ["0.0.0.0", "example.com", "localhost.", "127.1", "::1"])
def test_reject_noncanonical_host(host: str) -> None:
    with pytest.raises(ValueError):
        LocalHttpPolicy(host, 8000)


@pytest.mark.parametrize("port", [0, 65536, True])
def test_reject_invalid_port(port: int) -> None:
    with pytest.raises(ValueError):
        LocalHttpPolicy("localhost", port)


def test_canonical_origin() -> None:
    assert LocalHttpPolicy("[::1]", 8000).origin == "http://[::1]:8000"
    assert LocalHttpPolicy("localhost", 443, "https").origin == "https://localhost"
    with pytest.raises(ValueError):
        LocalHttpPolicy("localhost", 8000, "ftp")


@pytest.mark.parametrize(
    ("method", "headers", "expected"),
    [
        ("GET", [(b"host", b"localhost:8000")], True),
        ("GET", [], False),
        ("GET", [(b"host", b"evil.example")], False),
        ("GET", [(b"host", b"localhost:8000"), (b"host", b"localhost:8000")], False),
        ("POST", [(b"host", b"localhost:8000")], False),
        (
            "POST",
            [(b"host", b"localhost:8000"), (b"origin", b"http://localhost:8000")],
            True,
        ),
        (
            "POST",
            [(b"host", b"localhost:8000"), (b"origin", b"http://evil.example")],
            False,
        ),
        (
            "GET",
            [(b"host", b"evil.example"), (b"x-forwarded-host", b"localhost:8000")],
            False,
        ),
        (
            "POST",
            [
                (b"host", b"localhost:8000"),
                (b"origin", b"http://localhost:8000"),
                (b"origin", b"http://localhost:8000"),
            ],
            False,
        ),
    ],
)
def test_raw_headers(
    method: str, headers: list[tuple[bytes, bytes]], expected: bool
) -> None:
    assert LocalHttpPolicy("localhost", 8000).permits(method, headers) is expected
