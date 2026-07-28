from fastapi import APIRouter, HTTPException, Response, status

from app.modules.session.schemas import SessionResponse
from app.modules.session.store import get_session


router = APIRouter()


@router.get("/session/{session_id}", response_model=SessionResponse)
def get_analysis_session(session_id: str, response: Response) -> SessionResponse:
    response.headers["Cache-Control"] = "no-store, max-age=0"
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Analysis session was not found.",
            },
        )

    return SessionResponse(
        session_id=session.session_id,
        status=session.status,
        result=session.result,
        error=session.error,
        expires_at=session.expires_at,
    )
