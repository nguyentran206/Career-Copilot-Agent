from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from app.modules.analyze.helper import normalize_jd_text

from app.modules.analyze.schemas import AnalyzeStartResponse
from app.modules.analyze.service import validate_cv_file_bytes
from app.modules.session.service import run_analysis_session
from app.modules.session.store import create_session

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeStartResponse,
    status_code=202,
)
async def analyze_cv(
    background_tasks: BackgroundTasks,
    cv_file: UploadFile = File(...),
    jd_text: str = Form(...),
):
    normalized_jd_text = normalize_jd_text(jd_text)

    file_bytes = await cv_file.read()
    validate_cv_file_bytes(file_bytes)

    session = create_session()

    background_tasks.add_task(
        run_analysis_session,
        session_id=session.session_id,
        filename=cv_file.filename,
        content_type=cv_file.content_type,
        file_bytes=file_bytes,
        jd_text=normalized_jd_text,
    )

    return AnalyzeStartResponse(
        session_id=session.session_id,
        status="processing",
    )
