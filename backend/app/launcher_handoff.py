"""Trusted launcher handoff through an explicitly supplied private channel."""

from collections.abc import Callable

from app.local_bootstrap import LocalBootstrap


def deliver_bootstrap_challenge(
    bootstrap: LocalBootstrap,
    private_delivery: Callable[[str], None],
) -> None:
    """Deliver a challenge without returning it or writing it to logs.

    The caller must establish a private, authenticated local channel first.
    This adapter does not establish or verify the transport itself.
    """
    token = bootstrap.issue()
    try:
        private_delivery(token)
    except Exception:
        # Invalidate even a partially delivered challenge on transport failure.
        bootstrap.invalidate()
        raise RuntimeError("Private bootstrap delivery failed") from None
