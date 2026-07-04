import httpx
from fastapi import HTTPException, UploadFile, status

from pydantic import ValidationError
from app.modules.analyze.schemas import DocumentParserResponse

from app.core.config import settings


async def parse_cv_with_document_parser(cv_file: UploadFile) -> DocumentParserResponse:
    file_bytes = await cv_file.read()

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

    files = {
        "file": (
            cv_file.filename,
            file_bytes,
            cv_file.content_type or "application/pdf",
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

    return response.json()