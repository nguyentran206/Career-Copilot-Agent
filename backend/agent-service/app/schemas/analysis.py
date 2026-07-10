from typing import Literal

from pydantic import BaseModel, Field, field_validator


FitLevel = Literal["high", "medium", "low"]
MatchLevel = Literal["strong", "partial", "missing"]


class AgentAnalyzeRequest(BaseModel):
    cv_text: str = Field(..., min_length=50)
    jd_text: str = Field(..., min_length=50)

    @field_validator("cv_text", "jd_text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 50:
            raise ValueError("Text must contain at least 50 non-whitespace characters.")
        return normalized


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