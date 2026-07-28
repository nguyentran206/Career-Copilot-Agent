import httpx
from time import perf_counter
from fastapi import HTTPException, status

from pydantic import ValidationError
from app.modules.analyze.schemas import (
    AgentAnalyzeResponse,
    AnalysisResultPayload,
    DocumentParseSummary,
    DocumentParserResponse,
)

from app.core.config import settings
from app.core.request_context import get_request_id, log_event
from app.modules.analyze.helper import normalize_jd_text


MIN_EXTRACTED_CV_TEXT_LENGTH = 50


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


def validate_jd_file_bytes(file_bytes: bytes) -> None:
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMPTY_JD_FILE",
                "message": "Uploaded Job Description file is empty.",
            },
        )

    if len(file_bytes) > settings.max_jd_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "JD_FILE_TOO_LARGE",
                "message": (
                    "Job Description file size exceeds "
                    f"{settings.max_jd_file_size_mb}MB limit."
                ),
            },
        )


def validate_pdf_metadata(
    filename: str | None,
    content_type: str | None,
    document_type: str,
) -> None:
    is_pdf_name = bool(filename and filename.lower().endswith(".pdf"))
    is_pdf_content = content_type in {"application/pdf", "application/octet-stream"}
    if is_pdf_name and is_pdf_content:
        return

    code = "CV_FILE_NOT_PDF" if document_type == "cv" else "JD_FILE_NOT_PDF"
    label = "CV" if document_type == "cv" else "Job Description"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code": code, "message": f"{label} must be a PDF file."},
    )


async def parse_cv_bytes_with_document_parser(
    filename: str | None,
    content_type: str | None,
    file_bytes: bytes,
    request_id: str | None = None,
) -> DocumentParserResponse:
    return await parse_document_bytes_with_document_parser(
        filename=filename,
        content_type=content_type,
        file_bytes=file_bytes,
        document_type="cv",
        request_id=request_id,
    )


async def parse_document_bytes_with_document_parser(
    filename: str | None,
    content_type: str | None,
    file_bytes: bytes,
    document_type: str,
    request_id: str | None = None,
) -> DocumentParserResponse:
    if document_type == "cv":
        validate_cv_file_bytes(file_bytes)
    else:
        validate_jd_file_bytes(file_bytes)

    files = {
        "file": (
            filename,
            file_bytes,
            content_type or "application/pdf",
        )
    }

    data = {"document_type": document_type}

    url = f"{settings.document_parser_service_url}/api/v1/parse-document"

    timeout = httpx.Timeout(
        settings.document_parser_timeout_seconds,
        connect=5.0,
    )

    correlation_id = request_id or get_request_id()
    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                files=files,
                data=data,
                headers={"X-Request-ID": correlation_id},
            )
    except httpx.TimeoutException as exc:
        log_event(
            "downstream_failed",
            request_id=correlation_id,
            downstream="document-parser-service",
            error_code="DOCUMENT_PARSER_TIMEOUT",
            duration_ms=round((perf_counter() - started) * 1000, 2),
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "DOCUMENT_PARSER_TIMEOUT",
                "message": "Document Parser Service exceeded the allowed processing time.",
            },
        ) from exc
    except httpx.RequestError as exc:
        log_event(
            "downstream_failed",
            request_id=correlation_id,
            downstream="document-parser-service",
            error_code="DOCUMENT_PARSER_UNAVAILABLE",
            duration_ms=round((perf_counter() - started) * 1000, 2),
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "DOCUMENT_PARSER_UNAVAILABLE",
                "message": "Document Parser Service is unavailable.",
            },
        ) from exc

    log_event(
        "downstream_completed",
        request_id=correlation_id,
        downstream="document-parser-service",
        status_code=response.status_code,
        duration_ms=round((perf_counter() - started) * 1000, 2),
    )
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
                "message": "Document Parser Service failed to parse the uploaded document.",
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
    request_id: str | None = None,
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

    timeout = httpx.Timeout(
        settings.agent_service_timeout_seconds,
        connect=5.0,
    )

    correlation_id = request_id or get_request_id()
    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"X-Request-ID": correlation_id},
            )
    except httpx.TimeoutException as exc:
        log_event(
            "downstream_failed",
            request_id=correlation_id,
            downstream="agent-service",
            error_code="AGENT_SERVICE_TIMEOUT",
            duration_ms=round((perf_counter() - started) * 1000, 2),
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "AGENT_SERVICE_TIMEOUT",
                "message": "Agent Service exceeded the allowed processing time.",
            },
        ) from exc
    except httpx.RequestError as exc:
        log_event(
            "downstream_failed",
            request_id=correlation_id,
            downstream="agent-service",
            error_code="AGENT_SERVICE_UNAVAILABLE",
            duration_ms=round((perf_counter() - started) * 1000, 2),
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "AGENT_SERVICE_UNAVAILABLE",
                "message": "Agent Service is unavailable.",
            },
        ) from exc

    log_event(
        "downstream_completed",
        request_id=correlation_id,
        downstream="agent-service",
        status_code=response.status_code,
        duration_ms=round((perf_counter() - started) * 1000, 2),
    )
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
    jd_text: str | None,
    jd_filename: str | None = None,
    jd_content_type: str | None = None,
    jd_file_bytes: bytes | None = None,
    request_id: str | None = None,
) -> AnalysisResultPayload:
    parse_result = await parse_cv_bytes_with_document_parser(
        filename=filename,
        content_type=content_type,
        file_bytes=file_bytes,
        request_id=request_id,
    )

    jd_parse_result = None
    effective_jd_text = jd_text
    if jd_file_bytes is not None:
        jd_parse_result = await parse_document_bytes_with_document_parser(
            filename=jd_filename,
            content_type=jd_content_type,
            file_bytes=jd_file_bytes,
            document_type="jd",
            request_id=request_id,
        )
        effective_jd_text = normalize_jd_text(jd_parse_result.text)

    if effective_jd_text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "JD_INPUT_REQUIRED",
                "message": "Provide Job Description text or a PDF file.",
            },
        )

    analysis_result = await analyze_cv_with_agent_service(
        cv_text=parse_result.text,
        jd_text=effective_jd_text,
        parser_warnings=parse_result.warnings,
        request_id=request_id,
    )

    return AnalysisResultPayload(
        cv_parse_result=DocumentParseSummary(
            filename=parse_result.filename,
            document_type=parse_result.document_type,
            content_type=parse_result.content_type,
            file_size_bytes=parse_result.file_size_bytes,
            page_count=parse_result.page_count,
            text_length=parse_result.text_length,
            warnings=parse_result.warnings,
        ),
        jd_parse_result=(
            DocumentParseSummary(
                filename=jd_parse_result.filename,
                document_type=jd_parse_result.document_type,
                content_type=jd_parse_result.content_type,
                file_size_bytes=jd_parse_result.file_size_bytes,
                page_count=jd_parse_result.page_count,
                text_length=jd_parse_result.text_length,
                warnings=jd_parse_result.warnings,
            )
            if jd_parse_result
            else None
        ),
        analysis_result=analysis_result,
    )
