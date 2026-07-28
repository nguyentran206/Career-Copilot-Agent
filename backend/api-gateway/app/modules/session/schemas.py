from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.modules.analyze.schemas import AnalysisResultPayload


SessionStatus = Literal["processing", "completed", "failed"]


class SessionError(BaseModel):
    code: str
    message: str
    detail: dict | list | str | None = None


class AnalysisSession(BaseModel):
    session_id: str
    status: SessionStatus
    result: AnalysisResultPayload | None = None
    error: SessionError | None = None
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


class SessionResponse(BaseModel):
    session_id: str
    status: SessionStatus
    result: AnalysisResultPayload | None = None
    error: SessionError | None = None
    expires_at: datetime

