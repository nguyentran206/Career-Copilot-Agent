import httpx
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


async def parse_cv_with_document_parser(cv_file: UploadFile) -> dict:
    file_bytes = await cv_file.read()

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
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "code": "DOCUMENT_PARSER_ERROR",
                "message": "Document Parser Service failed to parse the uploaded CV.",
                "parser_detail": response.json(),
            },
        )

    return response.json()