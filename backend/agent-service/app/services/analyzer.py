from app.schemas.analysis import (
    AgentAnalyzeRequest,
    AgentAnalyzeResponse,
    ParsedCV,
    ParsedJD,
    ScoreBreakdown,
)
from app.services.matcher import match_required_skills
from app.services.parser import parse_cv_text, parse_jd_text
from app.services.scorer import (
    calculate_fit_score,
    calculate_required_skill_score,
    evaluate_fit_level,
)


def analyze_cv_against_jd(request: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
    parsed_cv_dict = parse_cv_text(request.cv_text)
    parsed_jd_dict = parse_jd_text(request.jd_text)

    parsed_cv = ParsedCV(**parsed_cv_dict)
    parsed_jd = ParsedJD(**parsed_jd_dict)

    skill_matches = match_required_skills(
        required_skills=parsed_jd.required_skills,
        cv_skills=parsed_cv.skills,
    )

    required_skill_score = calculate_required_skill_score(skill_matches)

    score_breakdown = ScoreBreakdown(
        required_skill_score=required_skill_score,
        preferred_skill_score=0.0,
        experience_relevance_score=0.0,
        project_domain_relevance_score=0.0,
        education_cert_tool_score=0.0,
    )

    fit_score = calculate_fit_score(score_breakdown)

    matched_skills = [
        match.jd_skill
        for match in skill_matches
        if match.match_level in {"strong", "partial"}
    ]

    missing_skills = [
        match.jd_skill
        for match in skill_matches
        if match.match_level == "missing"
    ]

    fit_level = evaluate_fit_level(
        fit_score=fit_score,
        missing_required_count=len(missing_skills),
    )

    suggestions = [
        f"Add stronger evidence for {skill} in your CV."
        for skill in missing_skills
    ]

    cover_letter = None
    learning_roadmap = None

    if fit_level in {"high", "medium"}:
        cover_letter = "Cover letter generation will be implemented in a later phase."

    if fit_level == "low":
        learning_roadmap = [
            f"Learn and practice {skill} with a small portfolio project."
            for skill in missing_skills
        ]

    return AgentAnalyzeResponse(
        fit_score=fit_score,
        fit_level=fit_level,
        score_breakdown=score_breakdown,
        parsed_cv=parsed_cv,
        parsed_jd=parsed_jd,
        skill_matches=skill_matches,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        cv_improvement_suggestions=suggestions,
        cover_letter=cover_letter,
        learning_roadmap=learning_roadmap,
    )