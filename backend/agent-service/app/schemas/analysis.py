from typing import Literal

from pydantic import BaseModel, Field, field_validator


FitLevel = Literal["high", "medium", "low"]
MatchLevel = Literal["strong", "partial", "missing"]
MatchType = Literal["exact", "alias", "taxonomy", "semantic", "none"]
SkillPriority = Literal["required", "preferred", "unknown"]
EvidenceSource = Literal["experience", "project", "skills", "mention"]


class LanguageInfo(BaseModel):
    primary_language: str = "unknown"
    detected_languages: list[str] = Field(default_factory=list)
    is_mixed_language: bool = False
    confidence: float = Field(default=0.0, ge=0, le=1)


class LocalizedEvidence(BaseModel):
    original_text: str = Field(..., exclude=True)
    source_language: str
    english_text: str | None = None


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


class CVEvidence(BaseModel):
    source: EvidenceSource
    text: str
    strength: float = Field(..., ge=0, le=1)
    source_language: str = "en"
    original_text: str | None = Field(default=None, exclude=True)


class JDSkillRequirement(BaseModel):
    skill: str
    classification: SkillPriority = "unknown"
    critical: bool = False
    evidence: str | None = None
    original_evidence: str | None = Field(default=None, exclude=True)
    english_evidence: str | None = None
    base_weight: float = Field(..., gt=0, le=1)


class SkillMatch(BaseModel):
    jd_skill: str
    resume_skill: str | None = None
    similarity: float = Field(..., ge=0, le=1)
    match_level: MatchLevel
    importance: float = Field(default=1.0, gt=0)
    classification: SkillPriority = "required"
    match_type: MatchType = "none"
    evidence: list[CVEvidence] = Field(default_factory=list)
    evidence_score: float = Field(default=0.0, ge=0, le=1)


class ComponentWeight(BaseModel):
    component: str
    configured_weight: float = Field(..., ge=0, le=1)
    enabled: bool
    effective_weight: float = Field(..., ge=0, le=1)


class ScoreBreakdown(BaseModel):
    required_skill_score: float = Field(..., ge=0, le=100)
    preferred_skill_score: float = Field(..., ge=0, le=100)
    experience_relevance_score: float = Field(..., ge=0, le=100)
    project_relevance_score: float = Field(..., ge=0, le=100)
    education_cert_relevance_score: float = Field(..., ge=0, le=100)
    unknown_skill_score: float = Field(default=0.0, ge=0, le=100)
    skill_coverage_score: float = Field(default=0.0, ge=0, le=100)
    component_weights: list[ComponentWeight] = Field(default_factory=list)


class ParsedCV(BaseModel):
    language_info: LanguageInfo = Field(default_factory=LanguageInfo)
    skills: list[str] = Field(default_factory=list)
    experience_summary: str | None = None
    experience_evidence: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    localized_evidence: list[LocalizedEvidence] = Field(default_factory=list)


class ParsedJD(BaseModel):
    language_info: LanguageInfo = Field(default_factory=LanguageInfo)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    unknown_skills: list[str] = Field(default_factory=list)
    skill_requirements: list[JDSkillRequirement] = Field(default_factory=list)
    job_title: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    experience_requirements: list[str] = Field(default_factory=list)
    project_requirements: list[str] = Field(default_factory=list)
    education_requirements: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)


class SkillWeightSource(BaseModel):
    skill: str
    jd_classification: SkillPriority
    jd_base_weight: float = Field(..., gt=0, le=1)
    final_weight: float = Field(..., gt=0, le=1)
    cv_evidence_score: float = Field(..., ge=0, le=1)
    contribution: float = Field(..., ge=0, le=1)


class ScoreAdjustment(BaseModel):
    rule: str
    reason: str
    score_before: float = Field(..., ge=0, le=100)
    score_after: float = Field(..., ge=0, le=100)


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

    raw_fit_score: float = Field(default=0.0, ge=0, le=100)
    score_confidence: float = Field(default=0.0, ge=0, le=1)
    scoring_version: str = "phase6-v2"
    skill_weight_sources: list[SkillWeightSource] = Field(default_factory=list)
    score_adjustments: list[ScoreAdjustment] = Field(default_factory=list)
    analysis_warnings: list[str] = Field(default_factory=list)
