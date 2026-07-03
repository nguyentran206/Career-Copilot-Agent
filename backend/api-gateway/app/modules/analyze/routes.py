from fastapi import APIRouter, File, Form, UploadFile

from app.modules.analyze.schemas import AnalyzeResponse, CVParseSummary
from app.modules.analyze.service import parse_cv_with_document_parser

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_cv(
    cv_file: UploadFile = File(...),
    jd_text: str = Form(...),
):
    parse_result = await parse_cv_with_document_parser(cv_file)

    cv_text = parse_result.get("text", "")
    text_preview = cv_text[:300] if cv_text else None

    return AnalyzeResponse(
        status="completed",
        message="CV parsed successfully. Agent analysis is not implemented yet.",
        cv_parse_result=CVParseSummary(
            filename=parse_result["filename"],
            document_type=parse_result.get("document_type"),
            content_type=parse_result.get("content_type"),
            file_size_bytes=parse_result["file_size_bytes"],
            page_count=parse_result["page_count"],
            text_length=parse_result["text_length"],
            warnings=parse_result.get("warnings", []),
        ),
        jd_text_length=len(jd_text),
        text_preview=text_preview,
    )