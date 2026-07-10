from app.schemas.analysis import ScoreBreakdown, SkillMatch


def calculate_required_skill_score(skill_matches: list[SkillMatch]) -> float:
    if not skill_matches:
        return 0.0

    weighted_sum = sum(match.similarity * match.importance for match in skill_matches)
    total_weight = sum(match.importance for match in skill_matches)

    return round((weighted_sum / total_weight) * 100, 2)


def calculate_fit_score(score_breakdown: ScoreBreakdown) -> float:
    score = (
        score_breakdown.required_skill_score * 0.45
        + score_breakdown.preferred_skill_score * 0.20
        + score_breakdown.experience_relevance_score * 0.15
        + score_breakdown.project_domain_relevance_score * 0.10
        + score_breakdown.education_cert_tool_score * 0.10
    )

    return round(score, 2)


def evaluate_fit_level(fit_score: float, missing_required_count: int) -> str:
    if fit_score >= 75:
        level = "high"
    elif fit_score >= 50:
        level = "medium"
    else:
        level = "low"

    if missing_required_count >= 2 and level == "high":
        return "medium"

    if missing_required_count >= 4:
        return "low"

    return level