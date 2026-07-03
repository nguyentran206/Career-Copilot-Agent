from pydantic import BaseModel, Field


class CVParseSummary(BaseModel):
    filename: str
    document_type: str | None = None
    content_type: str | None = None
    file_size_bytes: int
    page_count: int
    text_length: int
    warnings: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    status: str
    message: str
    cv_parse_result: CVParseSummary
    jd_text_length: int
    text_preview: str | None = None