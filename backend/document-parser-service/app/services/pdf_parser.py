import fitz
from fastapi import HTTPException, status

from app.core.config import settings


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int, list[str]]:
    warnings: list[str] = []

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PDF",
                "message": "The uploaded file is not a valid PDF.",
            },
        )

    try:
        if doc.needs_pass:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "ENCRYPTED_PDF",
                    "message": "Password-protected PDFs are not supported.",
                },
            )

        page_count = doc.page_count
        texts: list[str] = []

        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                texts.append(page_text.strip())

        text = "\n\n".join(texts).strip()

        if len(text) < settings.min_extracted_text_length:
            warnings.append("NO_TEXT_EXTRACTED_OR_SCANNED_PDF")

        return text, page_count, warnings

    finally:
        doc.close()