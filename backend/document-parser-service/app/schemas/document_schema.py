from pydantic import BaseModel


class ParseDocumentResponse(BaseModel):
    filename: str
    document_type: str | None = None
    content_type: str | None = None
    file_size_bytes: int
    page_count: int
    text: str
    text_length: int
    warnings: list[str] = []