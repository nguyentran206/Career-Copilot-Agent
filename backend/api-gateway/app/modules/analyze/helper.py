from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
import re


MIN_JD_TEXT_LENGTH = 50
MAX_JD_TEXT_LENGTH = 20000


def normalize_jd_text(jd_text: str) -> str:
    normalized = re.sub(r"\s+", " ", jd_text).strip()

    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "JD_TEXT_REQUIRED",
                "message": "Job Description text is required.",
            },
        )

    if len(normalized) < MIN_JD_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "JD_TEXT_TOO_SHORT",
                "message": f"Job Description text must be at least {MIN_JD_TEXT_LENGTH} characters.",
            },
        )

    if len(normalized) > MAX_JD_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "JD_TEXT_TOO_LONG",
                "message": f"Job Description text must not exceed {MAX_JD_TEXT_LENGTH} characters.",
            },
        )

    return normalized