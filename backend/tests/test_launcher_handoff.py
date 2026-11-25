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


def test_stale_delivery_failure_preserves_newer_challenge():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    newer_tokens = []

    def fail_after_reissue(token):
        newer_tokens.append(bootstrap.issue())
        raise ValueError(token)

    with pytest.raises(RuntimeError, match="^Private bootstrap delivery failed$") as error:
        deliver_bootstrap_challenge(bootstrap, fail_after_reissue)
    assert error.value.__context__ is None
    assert bootstrap.exchange(newer_tokens[0]) is not None


def test_token_specific_revocation_is_idempotent():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    token = bootstrap.issue()
    bootstrap.invalidate_token(token)
    bootstrap.invalidate_token(token)
    assert bootstrap.exchange(token) is None
    assert bootstrap.exchange(bootstrap.issue()) is not None


def test_exchange_is_blocked_until_delivery_returns():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    delivered = []

    def deliver(token):
        assert bootstrap.exchange(token) is None
        delivered.append(token)

    deliver_bootstrap_challenge(bootstrap, deliver)
    assert bootstrap.exchange(delivered[0]) is not None


def test_early_exchange_and_failed_delivery_never_issue_session():
    sessions = SessionStore(max_sessions=1)
    bootstrap = LocalBootstrap(sessions, "owner")

    def fail(token):
        assert bootstrap.exchange(token) is None
        raise ValueError("transport failed")

    with pytest.raises(RuntimeError, match="Private bootstrap delivery failed"):
        deliver_bootstrap_challenge(bootstrap, fail)
    assert bootstrap.exchange(bootstrap.issue()) is not None


def test_expired_delivery_cannot_activate():
    now = [0.0]
    bootstrap = LocalBootstrap(SessionStore(), "owner", 10, lambda: now[0])
    delivered = []

    def deliver(token):
        delivered.append(token)
        now[0] = 10.0

    with pytest.raises(RuntimeError, match="Private bootstrap delivery failed"):
        deliver_bootstrap_challenge(bootstrap, deliver)
    assert bootstrap.exchange(delivered[0]) is None


def test_stale_success_cannot_activate_or_revoke_newer_pending_token():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    newer_tokens = []

    def deliver(token):
        newer_tokens.append(bootstrap.prepare())

    with pytest.raises(RuntimeError, match="Private bootstrap delivery failed"):
        deliver_bootstrap_challenge(bootstrap, deliver)
    assert bootstrap.exchange(newer_tokens[0]) is None
    assert bootstrap.activate(newer_tokens[0])
    assert bootstrap.exchange(newer_tokens[0]) is not None
