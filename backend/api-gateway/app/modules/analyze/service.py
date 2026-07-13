import httpx
from fastapi import HTTPException, UploadFile, status

from pydantic import ValidationError
from app.modules.analyze.schemas import (
    AgentAnalyzeResponse,
    AnalysisResultPayload,
    CVParseSummary,
    DocumentParserResponse,
)

from app.core.config import settings


MIN_EXTRACTED_CV_TEXT_LENGTH = 50


async def parse_cv_with_document_parser(cv_file: UploadFile) -> DocumentParserResponse:
    file_bytes = await cv_file.read()

    return await parse_cv_bytes_with_document_parser(
        filename=cv_file.filename,
        content_type=cv_file.content_type,
        file_bytes=file_bytes,
    )


def validate_cv_file_bytes(
    file_bytes: bytes,
) -> None:
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMPTY_CV_FILE",
                "message": "Uploaded CV file is empty.",
            },
        )

    if len(file_bytes) > settings.max_cv_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "CV_FILE_TOO_LARGE",
                "message": f"CV file size exceeds {settings.max_cv_file_size_mb}MB limit.",
            },
        )


async def parse_cv_bytes_with_document_parser(
    filename: str | None,
    content_type: str | None,
    file_bytes: bytes,
) -> DocumentParserResponse:
    validate_cv_file_bytes(file_bytes)

    files = {
        "file": (
            filename,
            file_bytes,
            content_type or "application/pdf",
        )
    }

    data = {
        "document_type": "cv"
    }

    url = f"{settings.document_parser_service_url}/api/v1/parse-document"

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, files=files, data=data)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "DOCUMENT_PARSER_UNAVAILABLE",
                "message": "Document Parser Service is unavailable.",
            },
        ) from exc

    if response.status_code >= 400:
        try:
            parser_detail = response.json()
        except ValueError:
            parser_detail = {
                "raw_response": response.text[:500]
            }

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "code": "DOCUMENT_PARSER_ERROR",
                "message": "Document Parser Service failed to parse the uploaded CV.",
                "parser_detail": parser_detail,
            },
        )

    try:
        return DocumentParserResponse(**response.json())
    except (ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "DOCUMENT_PARSER_INVALID_RESPONSE",
                "message": "Document Parser Service returned an invalid response.",
            },
        ) from exc


async def analyze_cv_with_agent_service(
    cv_text: str,
    jd_text: str,
    parser_warnings: list[str] | None = None,
) -> AgentAnalyzeResponse:
    normalized_cv_text = " ".join(cv_text.split())

    if len(normalized_cv_text) < MIN_EXTRACTED_CV_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CV_TEXT_TOO_SHORT",
                "message": (
                    "Extracted CV text is too short for analysis. "
                    "The PDF may be scanned or image-based."
                ),
                "parser_warnings": parser_warnings or [],
            },
        )

    url = f"{settings.agent_service_url}/api/v1/analyze"

    payload = {
        "cv_text": normalized_cv_text,
        "jd_text": jd_text,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, json=payload)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "AGENT_SERVICE_UNAVAILABLE",
                "message": "Agent Service is unavailable.",
            },
        ) from exc

    if response.status_code >= 400:
        try:
            agent_detail = response.json()
        except ValueError:
            agent_detail = {
                "raw_response": response.text[:500]
            }

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "code": "AGENT_SERVICE_ERROR",
                "message": "Agent Service failed to analyze the CV and Job Description.",
                "agent_detail": agent_detail,
            },
        )

    try:
        return AgentAnalyzeResponse(**response.json())
    except (ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "AGENT_SERVICE_INVALID_RESPONSE",
                "message": "Agent Service returned an invalid response.",
            },
        ) from exc


async def run_analysis(
    filename: str | None,
    content_type: str | None,
    file_bytes: bytes,
    jd_text: str,
) -> AnalysisResultPayload:
    parse_result = await parse_cv_bytes_with_document_parser(
        filename=filename,
        content_type=content_type,
        file_bytes=file_bytes,
    )

    analysis_result = await analyze_cv_with_agent_service(
        cv_text=parse_result.text,
        jd_text=jd_text,
        parser_warnings=parse_result.warnings,
    )

    return AnalysisResultPayload(
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
