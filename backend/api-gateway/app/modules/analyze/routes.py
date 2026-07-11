from fastapi import APIRouter, File, Form, UploadFile
from app.modules.analyze.helper import normalize_jd_text

from app.modules.analyze.schemas import AnalyzeResponse, CVParseSummary
from app.modules.analyze.service import (
    analyze_cv_with_agent_service,
    parse_cv_with_document_parser,
)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_cv(
    cv_file: UploadFile = File(...),
    jd_text: str = Form(...),
):
    normalized_jd_text = normalize_jd_text(jd_text)

    parse_result = await parse_cv_with_document_parser(cv_file)

    analysis_result = await analyze_cv_with_agent_service(
        cv_text=parse_result.text,
        jd_text=normalized_jd_text,
        parser_warnings=parse_result.warnings,
    )

    return AnalyzeResponse(
        status="completed",
        message="CV parsed and analyzed successfully.",
        cv_parse_result=CVParseSummary(
            filename=parse_result.filename,
            document_type=parse_result.document_type,
            content_type=parse_result.content_type,
            file_size_bytes=parse_result.file_size_bytes,
            page_count=parse_result.page_count,
            text_length=parse_result.text_length,
            warnings=parse_result.warnings,
        ),
        analysis_result=analysis_result,
    )
