from datetime import datetime, timezone
from uuid import uuid4

from app.modules.analyze.schemas import AnalysisResultPayload
from app.modules.session.schemas import AnalysisSession, SessionError


_sessions: dict[str, AnalysisSession] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_session() -> AnalysisSession:
    session_id = str(uuid4())
    now = _now()

    session = AnalysisSession(
        session_id=session_id,
        status="processing",
        result=None,
        error=None,
        created_at=now,
        updated_at=now,
    )

    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> AnalysisSession | None:
    return _sessions.get(session_id)


def mark_session_completed(
    session_id: str,
    result: AnalysisResultPayload,
) -> AnalysisSession | None:
    session = get_session(session_id)
    if session is None:
        return None

    session.status = "completed"
    session.result = result
    session.error = None
    session.updated_at = _now()
    return session


def mark_session_failed(
    session_id: str,
    error: SessionError,
) -> AnalysisSession | None:
    session = get_session(session_id)
    if session is None:
        return None

    session.status = "failed"
    session.result = None
    session.error = error
    session.updated_at = _now()
    return session


def clear_sessions() -> None:
    _sessions.clear()

