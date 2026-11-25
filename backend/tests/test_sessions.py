"""Regression tests for the isolated session lifecycle."""

import pytest

from app.sessions import SessionStore


def test_session_and_csrf_binding():
    store = SessionStore()
    first = store.issue("first")
    second = store.issue("second")
    assert store.authenticate(first.session_token) == "first"
    assert store.authorize_mutation(first.session_token, first.csrf_token) == "first"
    assert store.authorize_mutation(first.session_token, second.csrf_token) is None
    assert store.authorize_mutation(first.session_token, None) is None
    assert store.authorize_mutation(first.session_token, "") is None
    assert store.authenticate("unknown") is None


def test_expiry_at_boundary():
    now = [0.0]
    store = SessionStore(lifetime_seconds=10, clock=lambda: now[0])
    credentials = store.issue("user")
    now[0] = 9.0
    assert store.authenticate(credentials.session_token) == "user"
    now[0] = 10.0
    assert store.authenticate(credentials.session_token) is None


def test_revocation_and_restart():
    store = SessionStore()
    credentials = store.issue("user")
    assert SessionStore().authenticate(credentials.session_token) is None
    store.revoke(credentials.session_token)
    store.revoke(credentials.session_token)
    assert store.authenticate(credentials.session_token) is None


def test_capacity_and_expired_cleanup():
    now = [0.0]
    store = SessionStore(lifetime_seconds=1, max_sessions=1, clock=lambda: now[0])
    store.issue("user")
    with pytest.raises(RuntimeError):
        store.issue("user")
    now[0] = 1.0
    assert store.authenticate(store.issue("user").session_token) == "user"


@pytest.mark.parametrize("lifetime, capacity", [(0, 1), (1, 0), (-1, 1)])
def test_invalid_limits(lifetime, capacity):
    with pytest.raises(ValueError):
        SessionStore(lifetime_seconds=lifetime, max_sessions=capacity)
