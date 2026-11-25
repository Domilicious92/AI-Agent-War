"""Process-local session lifecycle; no HTTP routes or credential verification."""

import hashlib
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class SessionCredentials:
    session_token: str
    csrf_token: str


@dataclass(frozen=True)
class _Session:
    principal_id: str
    csrf_digest: bytes
    expires_at: float


def _digest(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()


class SessionStore:
    """Issue only after trusted authentication; restart invalidates all sessions."""

    def __init__(
        self,
        lifetime_seconds: int = 3600,
        max_sessions: int = 128,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if lifetime_seconds <= 0 or max_sessions <= 0:
            raise ValueError("Session limits must be positive")
        self._lifetime = lifetime_seconds
        self._capacity = max_sessions
        self._clock = clock
        self._sessions: dict[bytes, _Session] = {}
        self._lock = Lock()

    def issue(self, principal_id: str) -> SessionCredentials:
        """Called by trusted server code only, never directly from client input."""
        if not principal_id:
            raise ValueError("Principal required")
        credentials = SessionCredentials(secrets.token_urlsafe(32), secrets.token_urlsafe(32))
        with self._lock:
            now = self._clock()
            self._sessions = {
                key: value for key, value in self._sessions.items() if value.expires_at > now
            }
            if len(self._sessions) >= self._capacity:
                raise RuntimeError("Session capacity reached")
            self._sessions[_digest(credentials.session_token)] = _Session(
                principal_id, _digest(credentials.csrf_token), now + self._lifetime
            )
        return credentials

    def authenticate(self, session_token: str, csrf_token: str | None = None) -> str | None:
        """Resolve a session; when supplied, require its matching CSRF token."""
        if not session_token or len(session_token) > 128:
            return None
        with self._lock:
            key = _digest(session_token)
            session = self._sessions.get(key)
            if session is None:
                return None
            if session.expires_at <= self._clock():
                del self._sessions[key]
                return None
            if csrf_token is not None and (
                not csrf_token
                or len(csrf_token) > 128
                or not secrets.compare_digest(session.csrf_digest, _digest(csrf_token))
            ):
                return None
            return session.principal_id

    def authorize_mutation(self, session_token: str, csrf_token: str | None) -> str | None:
        """Fail closed when the required CSRF token is absent."""
        if not csrf_token:
            return None
        return self.authenticate(session_token, csrf_token)

    def revoke(self, session_token: str) -> None:
        """Invalidate future lookups; in-flight operations need separate controls."""
        if session_token and len(session_token) <= 128:
            with self._lock:
                self._sessions.pop(_digest(session_token), None)
