"""Regression tests for the trusted local bootstrap boundary."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from app.local_bootstrap import LocalBootstrap
from app.sessions import SessionStore


def test_exchange_binds_server_identity_and_rejects_replay():
    sessions = SessionStore()
    bootstrap = LocalBootstrap(sessions, "local-owner")
    token = bootstrap.issue()
    credentials = bootstrap.exchange(token)
    assert credentials is not None
    assert sessions.authenticate(credentials.session_token) == "local-owner"
    assert bootstrap.exchange(token) is None


def test_expiry_at_exact_boundary():
    now = [0.0]
    bootstrap = LocalBootstrap(SessionStore(), "owner", 10, lambda: now[0])
    token = bootstrap.issue()
    now[0] = 10.0
    assert bootstrap.exchange(token) is None


def test_reissue_invalidates_previous_challenge():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    previous = bootstrap.issue()
    current = bootstrap.issue()
    assert bootstrap.exchange(previous) is None
    assert bootstrap.exchange(current) is not None


@pytest.mark.parametrize("invalid", ["", "x" * 129, "ä", "incorrect"])
def test_invalid_challenge_does_not_consume_valid_one(invalid):
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    token = bootstrap.issue()
    assert bootstrap.exchange(invalid) is None
    assert bootstrap.exchange(token) is not None


def test_concurrent_exchange_has_exactly_one_winner():
    bootstrap = LocalBootstrap(SessionStore(), "owner")
    token = bootstrap.issue()
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(bootstrap.exchange, [token] * 8))
    assert sum(result is not None for result in results) == 1


def test_capacity_failure_consumes_challenge():
    sessions = SessionStore(max_sessions=1)
    existing = sessions.issue("owner")
    bootstrap = LocalBootstrap(sessions, "owner")
    token = bootstrap.issue()
    with pytest.raises(RuntimeError):
        bootstrap.exchange(token)
    sessions.revoke(existing.session_token)
    assert bootstrap.exchange(token) is None


@pytest.mark.parametrize("principal,lifetime", [("", 120), ("owner", 0), ("owner", True)])
def test_invalid_configuration(principal, lifetime):
    with pytest.raises(ValueError):
        LocalBootstrap(SessionStore(), principal, lifetime)
