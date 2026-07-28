from dataclasses import dataclass
import json
import operator
import re
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.core.config import Settings
from app.schemas.analysis import (
    AgentAnalyzeRequest,
    ParsedCV,
    ParsedJD,
    ScoreBreakdown,
    SkillMatch,
    SkillWeightSource,
)
from app.services.gemini import (
    DisabledGeminiService,
    GeminiService,
)
from app.services.language import needs_english_canonicalization
from app.services.matcher import match_skills
from app.services.parser import parse_cv_text, parse_jd_text
from app.services.scorer import (
    apply_fit_guardrails,
    build_score_breakdown,
    calculate_fit_score,
    evaluate_fit_level,
)
from app.services.similarity import (
    FallbackSimilarityProvider,
    GeminiEmbeddingSimilarityProvider,
    LexicalSimilarityProvider,
    SimilarityProvider,
)


@dataclass
class WorkflowServices:
    settings: Settings
    gemini: DisabledGeminiService | GeminiService
    similarity: SimilarityProvider


class AnalysisState(TypedDict, total=False):
    request: AgentAnalyzeRequest
    parsed_cv: ParsedCV
    parsed_jd: ParsedJD
    skill_matches: list[SkillMatch]
    score_breakdown: ScoreBreakdown
    skill_weight_sources: list[SkillWeightSource]
    raw_fit_score: float
    fit_score: float
    fit_level: Literal["high", "medium", "low"]
    score_adjustments: list
    score_confidence: float
    suggestions: list[str]
    cover_letter: str | None
    learning_roadmap: list[str] | None
    cv_parse_succeeded: bool
    jd_parse_succeeded: bool
    embedding_succeeded: bool
    warnings: Annotated[list[str], operator.add]
    multilingual_fallback: Annotated[bool, operator.or_]


def build_default_services(settings: Settings) -> WorkflowServices:
    gemini = DisabledGeminiService()
    similarity: SimilarityProvider = LexicalSimilarityProvider()
    if settings.gemini_enabled and settings.gemini_api_key:
        gemini = GeminiService(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            timeout_seconds=settings.gemini_timeout_seconds,
            rate_limit_cooldown_seconds=settings.gemini_rate_limit_cooldown_seconds,
            max_concurrent_requests=settings.gemini_max_concurrent_requests,
            fallback_model=settings.gemini_fallback_model,
            max_server_retries=settings.gemini_max_server_retries,
            retry_backoff_seconds=settings.gemini_retry_backoff_seconds,
        )
        if settings.gemini_embedding_enabled:
            similarity = FallbackSimilarityProvider(
                primary=GeminiEmbeddingSimilarityProvider(
                    api_key=settings.gemini_api_key,
                    model=settings.gemini_embedding_model,
                    timeout_seconds=settings.gemini_timeout_seconds,
                    rate_limit_cooldown_seconds=settings.gemini_rate_limit_cooldown_seconds,
                ),
                fallback=LexicalSimilarityProvider(),
                retry_after_seconds=settings.gemini_rate_limit_cooldown_seconds,
            )

    return WorkflowServices(
        settings=settings,
        gemini=gemini,
        similarity=similarity,
    )


def _token_similarity(left: str, right: str) -> float:
    left_tokens = set(re.findall(r"[a-z0-9+#.]+", left.lower()))
    right_tokens = set(re.findall(r"[a-z0-9+#.]+", right.lower()))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _relevance_score(
    queries: list[str],
    evidence: list[str],
    similarity: SimilarityProvider,
) -> float:
    if not queries or not evidence:
        return 0.0
    best_scores = []
    for query in queries:
        best_scores.append(
            max(
                max(_token_similarity(query, item), similarity.similarity(query, item))
                for item in evidence
            )
        )
    return round(100 * sum(best_scores) / len(best_scores), 2)


def _split_generated_steps(value: str) -> list[str]:
    steps = []
    for line in value.splitlines():
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        if cleaned:
            steps.append(cleaned)
    return steps[:8]


def build_analysis_graph(services: WorkflowServices):
    def safe_cv_fallback(parsed: ParsedCV) -> ParsedCV:
        return ParsedCV(
            language_info=parsed.language_info,
            skills=parsed.skills,
            localized_evidence=parsed.localized_evidence,
        )

    def safe_jd_fallback(parsed: ParsedJD) -> ParsedJD:
        requirements = [
            requirement.model_copy(
                update={
                    "classification": "unknown",
                    "critical": False,
                    "evidence": None,
                    "english_evidence": None,
                    "base_weight": 0.45,
                }
            )
            for requirement in parsed.skill_requirements
        ]
        return ParsedJD(
            language_info=parsed.language_info,
            unknown_skills=[item.skill for item in requirements],
            skill_requirements=requirements,
            job_title=parsed.job_title,
        )

    def parse_cv_node(state: AnalysisState) -> dict:
        request = state["request"]
        fallback = ParsedCV(**parse_cv_text(request.cv_text))
        result = services.gemini.parse_cv(request.cv_text)
        if isinstance(result.value, ParsedCV):
            return {
                "parsed_cv": result.value,
                "cv_parse_succeeded": True,
                "warnings": result.warnings,
            }
        multilingual = needs_english_canonicalization(fallback.language_info)
        warnings = list(result.warnings)
        if multilingual:
            warnings.append("MULTILINGUAL_NORMALIZATION_UNAVAILABLE")
        return {
            "parsed_cv": safe_cv_fallback(fallback) if multilingual else fallback,
            "warnings": warnings,
            "multilingual_fallback": multilingual,
            "cv_parse_succeeded": False,
        }

    def parse_jd_node(state: AnalysisState) -> dict:
        request = state["request"]
        fallback = ParsedJD(**parse_jd_text(request.jd_text))
        result = services.gemini.parse_jd(request.jd_text)
        if isinstance(result.value, ParsedJD):
            return {
                "parsed_jd": result.value,
                "jd_parse_succeeded": True,
                "warnings": result.warnings,
            }
        multilingual = needs_english_canonicalization(fallback.language_info)
        warnings = list(result.warnings)
        if multilingual:
            warnings.append("MULTILINGUAL_NORMALIZATION_UNAVAILABLE")
        return {
            "parsed_jd": safe_jd_fallback(fallback) if multilingual else fallback,
            "warnings": warnings,
            "multilingual_fallback": multilingual,
            "jd_parse_succeeded": False,
        }

    def prepare_similarity_node(state: AnalysisState) -> dict:
        parsed_cv = state["parsed_cv"]
        parsed_jd = state["parsed_jd"]
        texts = list(
            dict.fromkeys(
                [item.skill for item in parsed_jd.skill_requirements]
                + parsed_cv.skills
                + parsed_jd.experience_requirements
                + parsed_cv.experience_evidence
                + parsed_jd.project_requirements
                + parsed_cv.projects
                + parsed_jd.education_requirements
                + parsed_cv.education
                + parsed_cv.certifications
            )
        )
        warnings = services.similarity.prepare(texts)
        embedding_succeeded = (
            services.settings.gemini_embedding_enabled
            and "GEMINI_EMBEDDING_FALLBACK" not in warnings
        )
        return {
            "warnings": warnings,
            "embedding_succeeded": embedding_succeeded,
        }

    def match_skills_node(state: AnalysisState) -> dict:
        request = state["request"]
        matches = match_skills(
            requirements=state["parsed_jd"].skill_requirements,
            parsed_cv=state["parsed_cv"],
            cv_text=request.cv_text,
            similarity_provider=services.similarity,
            strong_threshold=services.settings.semantic_strong_threshold,
            partial_threshold=services.settings.semantic_partial_threshold,
        )
        return {"skill_matches": matches}

    def calculate_score_node(state: AnalysisState) -> dict:
        parsed_cv = state["parsed_cv"]
        parsed_jd = state["parsed_jd"]
        experience_enabled = bool(parsed_jd.experience_requirements)
        project_enabled = bool(parsed_jd.project_requirements)
        education_enabled = bool(parsed_jd.education_requirements)
        experience_score = _relevance_score(
            parsed_jd.experience_requirements,
            parsed_cv.experience_evidence,
            services.similarity,
        )
        project_score = _relevance_score(
            parsed_jd.project_requirements,
            parsed_cv.projects,
            services.similarity,
        )
        education_score = _relevance_score(
            parsed_jd.education_requirements,
            parsed_cv.education + parsed_cv.certifications,
            services.similarity,
        )
        breakdown, weight_sources = build_score_breakdown(
            requirements=parsed_jd.skill_requirements,
            matches=state["skill_matches"],
            experience_score=experience_score,
            project_score=project_score,
            education_score=education_score,
            experience_enabled=experience_enabled,
            project_enabled=project_enabled,
            education_enabled=education_enabled,
        )
        raw_score = calculate_fit_score(breakdown)
        fit_score, adjustments = apply_fit_guardrails(
            raw_score=raw_score,
            requirements=parsed_jd.skill_requirements,
            matches=state["skill_matches"],
            required_skill_score=breakdown.required_skill_score,
        )
        average_match_confidence = (
            sum(match.similarity for match in state["skill_matches"])
            / len(state["skill_matches"])
            if state["skill_matches"]
            else 0.0
        )
        score_confidence = min(
            1.0,
            0.50
            + 0.35 * average_match_confidence
            + (0.05 if state.get("cv_parse_succeeded") else 0)
            + (0.05 if state.get("jd_parse_succeeded") else 0),
        )
        if state.get("multilingual_fallback"):
            score_confidence = min(score_confidence, 0.40)
        return {
            "score_breakdown": breakdown,
            "skill_weight_sources": weight_sources,
            "raw_fit_score": raw_score,
            "fit_score": fit_score,
            "fit_level": evaluate_fit_level(fit_score),
            "score_adjustments": adjustments,
            "score_confidence": round(score_confidence, 2),
        }

    def suggest_improvements_node(state: AnalysisState) -> dict:
        missing = [
            match.jd_skill
            for match in state["skill_matches"]
            if match.match_level == "missing"
        ]
        suggestions = [
            f"Add concrete CV evidence for {skill} because it is stated in the JD."
            for skill in missing
        ]
        if not suggestions and state["fit_level"] == "medium":
            suggestions = [
                "Add measurable achievements and clearer responsibility evidence for the matched JD requirements."
            ]
        if not suggestions and state["fit_level"] == "low":
            suggestions = [
                "Add relevant skills, experience, and project evidence that directly match the Job Description."
            ]
        return {"suggestions": suggestions}

    def route_outcome(state: AnalysisState) -> Literal["generate_cover_letter", "generate_roadmap"]:
        return "generate_cover_letter" if state["fit_level"] in {"high", "medium"} else "generate_roadmap"

    def generate_cover_letter_node(state: AnalysisState) -> dict:
        matched = [
            match.jd_skill
            for match in state["skill_matches"]
            if match.match_level in {"strong", "partial"}
        ]
        fallback = (
            "I am applying for this opportunity because my background demonstrates "
            f"relevant evidence in {', '.join(matched) if matched else 'the stated job requirements'}. "
            "I would welcome the opportunity to discuss how my experience can support the team."
        )
        if not (
            state.get("cv_parse_succeeded")
            and state.get("jd_parse_succeeded")
        ):
            return {
                "cover_letter": fallback,
                "learning_roadmap": None,
                "warnings": [],
            }
        parsed_cv = state["parsed_cv"]
        context = {
            "job_title": state["parsed_jd"].job_title,
            "matched_requirements": matched,
            "skills": parsed_cv.skills,
            "experience_summary": parsed_cv.experience_summary,
            "experience_evidence": parsed_cv.experience_evidence[:8],
            "projects": parsed_cv.projects[:6],
            "education": parsed_cv.education[:4],
            "certifications": parsed_cv.certifications[:4],
        }
        generated = services.gemini.generate(
            "Write a concise truthful cover letter in English using only the "
            "validated context below. Do not invent experience or requirements. "
            "Return only the cover letter.\n\n"
            + json.dumps(context, ensure_ascii=False)
        )
        return {
            "cover_letter": generated.value
            if isinstance(generated.value, str)
            else fallback,
            "learning_roadmap": None,
            "warnings": generated.warnings,
        }

    def generate_roadmap_node(state: AnalysisState) -> dict:
        missing = [
            match.jd_skill
            for match in state["skill_matches"]
            if match.match_level == "missing"
        ]
        fallback = [
            f"Learn and practice {skill} with a small portfolio project."
            for skill in missing
        ] or [
            "Review the JD and identify its explicit technical requirements.",
            "Build a small project demonstrating the most relevant requirement.",
            "Update the CV with measurable outcomes from that project.",
        ]
        if not (
            state.get("cv_parse_succeeded")
            and state.get("jd_parse_succeeded")
        ):
            return {
                "cover_letter": None,
                "learning_roadmap": fallback,
                "warnings": [],
            }
        generated = services.gemini.generate(
            "Create a short numbered learning roadmap in English using only the "
            "missing JD requirements below. Include hands-on portfolio evidence and "
            "return one step per line.\n\n"
            + json.dumps(
                {
                    "job_title": state["parsed_jd"].job_title,
                    "missing_requirements": missing,
                },
                ensure_ascii=False,
            )
        )
        generated_steps = (
            _split_generated_steps(generated.value)
            if isinstance(generated.value, str)
            else []
        )
        return {
            "cover_letter": None,
            "learning_roadmap": generated_steps or fallback,
            "warnings": generated.warnings,
        }

    builder = StateGraph(AnalysisState)
    builder.add_node("parse_cv", parse_cv_node)
    builder.add_node("parse_jd", parse_jd_node)
    builder.add_node("prepare_similarity", prepare_similarity_node)
    builder.add_node("match_skills", match_skills_node)
    builder.add_node("calculate_score", calculate_score_node)
    builder.add_node("suggest_improvements", suggest_improvements_node)
    builder.add_node("generate_cover_letter", generate_cover_letter_node)
    builder.add_node("generate_roadmap", generate_roadmap_node)
    builder.add_edge(START, "parse_cv")
    builder.add_edge(START, "parse_jd")
    builder.add_edge("parse_cv", "prepare_similarity")
    builder.add_edge("parse_jd", "prepare_similarity")
    builder.add_edge("prepare_similarity", "match_skills")
    builder.add_edge("match_skills", "calculate_score")
    builder.add_edge("calculate_score", "suggest_improvements")
    builder.add_conditional_edges("suggest_improvements", route_outcome)
    builder.add_edge("generate_cover_letter", END)
    builder.add_edge("generate_roadmap", END)
    return builder.compile()
