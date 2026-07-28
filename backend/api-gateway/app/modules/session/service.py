from fastapi import HTTPException

from app.modules.analyze.service import run_analysis
from app.core.request_limits import analyze_request_limiter
from app.modules.session.schemas import SessionError
from app.modules.session.store import mark_session_completed, mark_session_failed


def build_session_error(exc: Exception) -> SessionError:
    if isinstance(exc, HTTPException):
        detail = exc.detail

        if isinstance(detail, dict):
            code = str(detail.get("code", "ANALYSIS_FAILED"))
            message = str(detail.get("message", "Unable to complete analysis."))
            return SessionError(code=code, message=message, detail=detail)

        return SessionError(
            code="ANALYSIS_FAILED",
            message="Unable to complete analysis.",
            detail=detail,
        )

    return SessionError(
        code="ANALYSIS_FAILED",
        message="Unable to complete analysis.",
        detail=None,
    )


async def run_analysis_session(
    session_id: str,
    filename: str | None,
    content_type: str | None,
    file_bytes: bytes,
    jd_text: str | None,
    request_id: str,
    jd_filename: str | None = None,
    jd_content_type: str | None = None,
    jd_file_bytes: bytes | None = None,
) -> None:
    try:
        try:
            result = await run_analysis(
                filename=filename,
                content_type=content_type,
                file_bytes=file_bytes,
                jd_text=jd_text,
                jd_filename=jd_filename,
                jd_content_type=jd_content_type,
                jd_file_bytes=jd_file_bytes,
                request_id=request_id,
            )
        except Exception as exc:
            mark_session_failed(
                session_id=session_id,
                error=build_session_error(exc),
            )
            return

        mark_session_completed(
            session_id=session_id,
            result=result,
        )
    finally:
        analyze_request_limiter.release()

