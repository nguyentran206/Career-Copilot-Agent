from datetime import datetime, timedelta, timezone

import pytest

from app.modules.session.store import (
    SessionCapacityError,
    clear_sessions,
    create_session,
    get_session,
    mark_session_failed,
)
from app.modules.session.schemas import SessionError


@pytest.fixture(autouse=True)
def empty_store():
    clear_sessions()
    yield
    clear_sessions()


def test_session_expires_after_configured_ttl(monkeypatch):
    now = datetime(2026, 7, 28, tzinfo=timezone.utc)
    monkeypatch.setattr("app.modules.session.store._now", lambda: now)
    monkeypatch.setattr("app.modules.session.store.settings.session_ttl_minutes", 30)
    session = create_session()

    monkeypatch.setattr(
        "app.modules.session.store._now",
        lambda: now + timedelta(minutes=30, seconds=1),
    )
    assert get_session(session.session_id) is None


def test_terminal_state_resets_ttl(monkeypatch):
    now = datetime(2026, 7, 28, tzinfo=timezone.utc)
    monkeypatch.setattr("app.modules.session.store._now", lambda: now)
    session = create_session()
    completed_at = now + timedelta(minutes=10)
    monkeypatch.setattr("app.modules.session.store._now", lambda: completed_at)

    updated = mark_session_failed(
        session.session_id,
        SessionError(code="TEST", message="test"),
    )

    assert updated is not None
    assert updated.expires_at == completed_at + timedelta(minutes=30)


def test_capacity_is_enforced_after_lazy_cleanup(monkeypatch):
    monkeypatch.setattr("app.modules.session.store.settings.max_sessions", 1)
    create_session()

    with pytest.raises(SessionCapacityError):
        create_session()
