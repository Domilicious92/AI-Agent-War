"""Strict server-owned loopback HTTP authority configuration."""

from dataclasses import dataclass

from app.browser_origin import permits_browser_request

_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "[::1]"})


@dataclass(frozen=True)
class LocalHttpPolicy:
    """Use one explicit loopback authority; never trust forwarded headers."""

    host: str
    port: int
    scheme: str = "http"

    def __post_init__(self) -> None:
        if self.host not in _LOOPBACK_HOSTS:
            raise ValueError("Expected a canonical loopback host")
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ValueError("Invalid port")
        if self.scheme not in {"http", "https"}:
            raise ValueError("Invalid scheme")

    @property
    def authority(self) -> str:
        default_port = 443 if self.scheme == "https" else 80
        return self.host if self.port == default_port else f"{self.host}:{self.port}"

    @property
    def origin(self) -> str:
        return f"{self.scheme}://{self.authority}"

    def permits(self, method: str, headers: list[tuple[bytes, bytes]]) -> bool:
        """Preserve duplicate raw ASGI headers and reject ambiguous authority."""
        hosts = [value for name, value in headers if name.lower() == b"host"]
        if hosts != [self.authority.encode("ascii")]:
            return False
        origins = [
            value.decode("latin-1") for name, value in headers if name.lower() == b"origin"
        ]
        return permits_browser_request(method, origins, self.origin)
