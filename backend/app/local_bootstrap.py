"""One-time local bootstrap credentials, issued only by trusted server code."""

import hashlib
import secrets
import time
from collections.abc import Callable
from threading import Lock

from app.sessions import SessionCredentials, SessionStore


class LocalBootstrap:
    """Exchange a short-lived, single-use challenge for a server-owned identity."""

    def __init__(
        self,
        sessions: SessionStore,
        principal_id: str,
        lifetime_seconds: int = 120,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not principal_id or type(lifetime_seconds) is not int or lifetime_seconds <= 0:
            raise ValueError("Invalid bootstrap configuration")
        self._sessions = sessions
        self._principal_id = principal_id
        self._lifetime = lifetime_seconds
        self._clock = clock
        self._lock = Lock()
        self._digest: bytes | None = None
        self._expires_at = 0.0

    def issue(self) -> str:
        """Trusted local launcher only; never expose this method as an HTTP route."""
        token = secrets.token_urlsafe(32)
        with self._lock:
            self._digest = hashlib.sha256(token.encode("ascii")).digest()
            self._expires_at = self._clock() + self._lifetime
        return token

    def invalidate(self) -> None:
        """Revoke the outstanding challenge without issuing a replacement."""
        with self._lock:
            self._digest = None
            self._expires_at = 0.0

    def exchange(self, token: str) -> SessionCredentials | None:
        """Consume a valid challenge atomically, even if session issuance fails."""
        if not token or len(token) > 128 or not token.isascii():
            return None
        digest = hashlib.sha256(token.encode("ascii")).digest()
        with self._lock:
            if self._digest is None or self._clock() >= self._expires_at:
                self._digest = None
                return None
            if not secrets.compare_digest(self._digest, digest):
                return None
            self._digest = None
            return self._sessions.issue(self._principal_id)
