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
    except Exception:  # noqa: BLE001 - transport failures must revoke the challenge.
        # Invalidate even a partially delivered challenge on transport failure.
        bootstrap.invalidate_token(token)
    else:
        return
    # Raise outside the handler to avoid retaining the transport exception as context.
    raise RuntimeError("Private bootstrap delivery failed")
