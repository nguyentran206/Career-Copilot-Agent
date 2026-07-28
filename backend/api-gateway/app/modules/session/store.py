from datetime import datetime, timedelta, timezone
from threading import RLock
from uuid import uuid4

from app.modules.analyze.schemas import AnalysisResultPayload
from app.core.config import settings
from app.modules.session.schemas import AnalysisSession, SessionError


_sessions: dict[str, AnalysisSession] = {}
_lock = RLock()


class SessionCapacityError(RuntimeError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _expiry(now: datetime) -> datetime:
    return now + timedelta(minutes=settings.session_ttl_minutes)


def _purge_expired(now: datetime) -> int:
    expired_ids = [
        session_id
        for session_id, session in _sessions.items()
        if session.expires_at <= now
    ]
    for session_id in expired_ids:
        del _sessions[session_id]
    return len(expired_ids)


def create_session() -> AnalysisSession:
    with _lock:
        now = _now()
        _purge_expired(now)
        if len(_sessions) >= settings.max_sessions:
            raise SessionCapacityError("Temporary analysis session capacity reached.")
        session = AnalysisSession(
            session_id=str(uuid4()),
            status="processing",
            result=None,
            error=None,
            created_at=now,
            updated_at=now,
            expires_at=_expiry(now),
        )
        _sessions[session.session_id] = session
        return session.model_copy(deep=True)


def get_session(session_id: str) -> AnalysisSession | None:
    with _lock:
        now = _now()
        _purge_expired(now)
        session = _sessions.get(session_id)
        return session.model_copy(deep=True) if session else None


def mark_session_completed(
    session_id: str,
    result: AnalysisResultPayload,
) -> AnalysisSession | None:
    with _lock:
        now = _now()
        _purge_expired(now)
        session = _sessions.get(session_id)
        if session is None:
            return None
        session.status = "completed"
        session.result = result
        session.error = None
        session.updated_at = now
        session.expires_at = _expiry(now)
        return session.model_copy(deep=True)


def mark_session_failed(
    session_id: str,
    error: SessionError,
) -> AnalysisSession | None:
    with _lock:
        now = _now()
        _purge_expired(now)
        session = _sessions.get(session_id)
        if session is None:
            return None
        session.status = "failed"
        session.result = None
        session.error = error
        session.updated_at = now
        session.expires_at = _expiry(now)
        return session.model_copy(deep=True)


def clear_sessions() -> None:
    with _lock:
        _sessions.clear()

