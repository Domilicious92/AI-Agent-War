"""Fail-closed browser origin checks for future cookie-authenticated routes."""

from collections.abc import Sequence

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def permits_browser_request(
    method: str,
    origin_headers: Sequence[str],
    trusted_origin: str,
) -> bool:
    """Require one exact configured origin for every unsafe browser request.

    The trusted origin must come from validated server configuration, never
    from Host, Forwarded, or other client-controlled request headers.
    This helper is not authentication or a complete CSRF defense.
    """
    if not trusted_origin or trusted_origin == "null":
        return False
    if method in SAFE_METHODS:
        return not origin_headers or (
            len(origin_headers) == 1 and origin_headers[0] == trusted_origin
        )
    return len(origin_headers) == 1 and origin_headers[0] == trusted_origin
