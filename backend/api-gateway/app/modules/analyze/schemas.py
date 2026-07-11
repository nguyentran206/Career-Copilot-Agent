from pydantic import BaseModel, Field
from typing import Literal


FitLevel = Literal["high", "medium", "low"]
MatchLevel = Literal["strong", "partial", "missing"]


class CVParseSummary(BaseModel):
    filename: str
    document_type: str | None = None
    content_type: str | None = None
    file_size_bytes: int
    page_count: int
    text_length: int
    warnings: list[str] = Field(default_factory=list)


class DocumentParserResponse(BaseModel):
    filename: str
    document_type: str | None = None
    content_type: str | None = None
    file_size_bytes: int
    page_count: int
    text: str
    text_length: int
    warnings: list[str] = Field(default_factory=list)


class SkillMatch(BaseModel):
    jd_skill: str
    resume_skill: str | None = None
    similarity: float = Field(..., ge=0, le=1)
    match_level: MatchLevel
    importance: float = Field(default=1.0, gt=0)


class ScoreBreakdown(BaseModel):
    required_skill_score: float = Field(..., ge=0, le=100)
    preferred_skill_score: float = Field(..., ge=0, le=100)
    experience_relevance_score: float = Field(..., ge=0, le=100)
    project_domain_relevance_score: float = Field(..., ge=0, le=100)
    education_cert_tool_score: float = Field(..., ge=0, le=100)


class ParsedCV(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience_summary: str | None = None
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class ParsedJD(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)


class AgentAnalyzeResponse(BaseModel):
    fit_score: float = Field(..., ge=0, le=100)
    fit_level: FitLevel
    score_breakdown: ScoreBreakdown

    parsed_cv: ParsedCV
    parsed_jd: ParsedJD

    skill_matches: list[SkillMatch] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)

    cv_improvement_suggestions: list[str] = Field(default_factory=list)
    cover_letter: str | None = None
    learning_roadmap: list[str] | None = None


class AnalyzeResponse(BaseModel):
    status: str
    message: str
    cv_parse_result: CVParseSummary
    analysis_result: AgentAnalyzeResponse
