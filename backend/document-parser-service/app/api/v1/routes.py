from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.document_schema import ParseDocumentResponse
from app.services.pdf_parser import extract_text_from_pdf
from app.utils.file_validation import validate_upload_file

api_router = APIRouter()


@api_router.get("/health")
def health_check():
    return {
        "service": "document-parser-service",
        "status": "ok",
    }


@api_router.post("/parse-document", response_model=ParseDocumentResponse)
async def parse_document(
    file: UploadFile = File(...),
    document_type: str | None = Form(default=None),
):
    file_bytes = await validate_upload_file(file)

    text, page_count, warnings = extract_text_from_pdf(file_bytes)

    return ParseDocumentResponse(
        filename=file.filename,
        document_type=document_type,
        content_type=file.content_type,
        file_size_bytes=len(file_bytes),
        page_count=page_count,
        text=text,
        text_length=len(text),
        warnings=warnings,
    )