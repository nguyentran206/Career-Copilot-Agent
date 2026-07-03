from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


async def validate_upload_file(file: UploadFile) -> bytes:
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "FILE_REQUIRED",
                "message": "File is required.",
            },
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILENAME",
                "message": "Filename is required.",
            },
        )

    extension = file.filename.rsplit(".", 1)[-1].lower()

    if extension not in settings.allowed_extension_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "UNSUPPORTED_FILE_TYPE",
                "message": f"Only {settings.allowed_extensions} files are supported.",
            },
        )

    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CONTENT_TYPE",
                "message": "Only PDF content type is supported.",
            },
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMPTY_FILE",
                "message": "Uploaded file is empty.",
            },
        )

    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"File size exceeds {settings.max_file_size_mb}MB limit.",
            },
        )

    return content