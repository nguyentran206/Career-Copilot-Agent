from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from app.core.request_limits import (
    RequestLimitExceeded,
    analyze_request_limiter,
)
from app.modules.analyze.helper import normalize_jd_text

from app.modules.analyze.schemas import AnalyzeStartResponse
from app.modules.analyze.service import (
    validate_cv_file_bytes,
    validate_jd_file_bytes,
    validate_pdf_metadata,
)
from app.modules.session.service import run_analysis_session
from app.modules.session.store import SessionCapacityError, create_session

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeStartResponse,
    status_code=202,
)
async def analyze_cv(
    background_tasks: BackgroundTasks,
    request: Request,
    response: Response,
    cv_file: UploadFile = File(...),
    jd_text: str | None = Form(default=None),
    jd_file: UploadFile | None = File(default=None),
):
    has_jd_text = bool(jd_text and jd_text.strip())
    has_jd_file = jd_file is not None
    if has_jd_text and has_jd_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "JD_INPUT_CONFLICT",
                "message": "Provide either Job Description text or a PDF, not both.",
            },
        )
    if jd_text is None and not has_jd_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "JD_INPUT_REQUIRED",
                "message": "Provide Job Description text or a PDF file.",
            },
        )

    normalized_jd_text = normalize_jd_text(jd_text or "") if not has_jd_file else None

    validate_pdf_metadata(cv_file.filename, cv_file.content_type, "cv")
    file_bytes = await cv_file.read()
    validate_cv_file_bytes(file_bytes)

    jd_file_bytes = None
    if jd_file is not None:
        validate_pdf_metadata(jd_file.filename, jd_file.content_type, "jd")
        jd_file_bytes = await jd_file.read()
        validate_jd_file_bytes(jd_file_bytes)

    client_key = request.client.host if request.client else "unknown"
    try:
        analyze_request_limiter.reserve(client_key)
    except RequestLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": exc.code, "message": exc.message},
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc

    try:
        session = create_session()
    except SessionCapacityError as exc:
        analyze_request_limiter.release()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "SESSION_CAPACITY_REACHED",
                "message": "Temporary session storage is full. Please retry later.",
            },
            headers={"Retry-After": "30"},
        ) from exc

    background_tasks.add_task(
        run_analysis_session,
        session_id=session.session_id,
        filename=cv_file.filename,
        content_type=cv_file.content_type,
        file_bytes=file_bytes,
        jd_text=normalized_jd_text,
        jd_filename=jd_file.filename if jd_file else None,
        jd_content_type=jd_file.content_type if jd_file else None,
        jd_file_bytes=jd_file_bytes,
        request_id=request.state.request_id,
    )

    response.headers["Cache-Control"] = "no-store, max-age=0"
    return AnalyzeStartResponse(
        session_id=session.session_id,
        status="processing",
    )
