"""Exercise launcher handoff with a fake private transport."""

import pytest

from app.launcher_handoff import deliver_bootstrap_challenge
from app.local_bootstrap import LocalBootstrap
from app.sessions import SessionStore


def test_private_delivery_receives_single_use_challenge():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    delivered = []
    assert deliver_bootstrap_challenge(bootstrap, delivered.append) is None
    assert len(delivered) == 1
    assert bootstrap.exchange(delivered[0]) is not None
    assert bootstrap.exchange(delivered[0]) is None


def test_partial_delivery_failure_revokes_challenge():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    delivered = []

    def fail_after_delivery(token):
        delivered.append(token)
        raise ValueError(token)

    with pytest.raises(RuntimeError, match="^Private bootstrap delivery failed$"):
        deliver_bootstrap_challenge(bootstrap, fail_after_delivery)
    assert bootstrap.exchange(delivered[0]) is None


def test_explicit_revocation_is_idempotent():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    token = bootstrap.issue()
    bootstrap.invalidate()
    bootstrap.invalidate()
    assert bootstrap.exchange(token) is None
    assert bootstrap.exchange(bootstrap.issue()) is not None
