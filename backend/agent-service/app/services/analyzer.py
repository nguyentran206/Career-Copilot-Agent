from functools import lru_cache

from app.core.config import settings
from app.schemas.analysis import AgentAnalyzeRequest, AgentAnalyzeResponse
from app.services.workflow import build_analysis_graph, build_default_services


@lru_cache(maxsize=1)
def get_analysis_graph():
    return build_analysis_graph(build_default_services(settings))


def analyze_cv_against_jd(request: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
    state = get_analysis_graph().invoke(
        {"request": request, "warnings": [], "multilingual_fallback": False},
        {"recursion_limit": 30},
    )
    matches = state["skill_matches"]
    matched_skills = [
        match.jd_skill
        for match in matches
        if match.match_level in {"strong", "partial"}
    ]
    missing_skills = [
        match.jd_skill for match in matches if match.match_level == "missing"
    ]
    return AgentAnalyzeResponse(
        fit_score=state["fit_score"],
        raw_fit_score=state["raw_fit_score"],
        fit_level=state["fit_level"],
        score_confidence=state["score_confidence"],
        scoring_version=settings.scoring_version,
        score_breakdown=state["score_breakdown"],
        parsed_cv=state["parsed_cv"],
        parsed_jd=state["parsed_jd"],
        skill_matches=matches,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        cv_improvement_suggestions=state["suggestions"],
        cover_letter=state.get("cover_letter"),
        learning_roadmap=state.get("learning_roadmap"),
        skill_weight_sources=state["skill_weight_sources"],
        score_adjustments=state["score_adjustments"],
        analysis_warnings=list(dict.fromkeys(state.get("warnings", []))),
    )
