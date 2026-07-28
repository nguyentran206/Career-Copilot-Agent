from app.schemas.analysis import (
    ComponentWeight,
    JDSkillRequirement,
    ScoreAdjustment,
    ScoreBreakdown,
    SkillMatch,
    SkillWeightSource,
)


COMPONENT_WEIGHTS = {
    "skill_coverage_score": 0.65,
    "experience_relevance_score": 0.20,
    "project_relevance_score": 0.10,
    "education_cert_relevance_score": 0.05,
}


def _group_score(matches: list[SkillMatch], classification: str) -> float:
    group = [match for match in matches if match.classification == classification]
    if not group:
        return 0.0
    return round(100 * sum(match.evidence_score for match in group) / len(group), 2)


def calculate_skill_coverage(
    requirements: list[JDSkillRequirement],
    matches: list[SkillMatch],
) -> tuple[float, list[SkillWeightSource]]:
    match_lookup = {match.jd_skill.lower(): match for match in matches}
    total_weight = 0.0
    weighted_evidence = 0.0
    sources: list[SkillWeightSource] = []

    for requirement in requirements:
        match = match_lookup[requirement.skill.lower()]
        final_weight = requirement.base_weight
        contribution = final_weight * match.evidence_score
        total_weight += final_weight
        weighted_evidence += contribution
        sources.append(
            SkillWeightSource(
                skill=requirement.skill,
                jd_classification=requirement.classification,
                jd_base_weight=requirement.base_weight,
                final_weight=round(final_weight, 4),
                cv_evidence_score=match.evidence_score,
                contribution=round(contribution, 4),
            )
        )

    score = 0.0 if total_weight == 0 else 100 * weighted_evidence / total_weight
    return round(score, 2), sources


def build_score_breakdown(
    requirements: list[JDSkillRequirement],
    matches: list[SkillMatch],
    experience_score: float,
    project_score: float,
    education_score: float,
    experience_enabled: bool,
    project_enabled: bool,
    education_enabled: bool,
) -> tuple[ScoreBreakdown, list[SkillWeightSource]]:
    skill_score, weight_sources = calculate_skill_coverage(
        requirements=requirements,
        matches=matches,
    )
    enabled = {
        "skill_coverage_score": bool(requirements),
        "experience_relevance_score": experience_enabled,
        "project_relevance_score": project_enabled,
        "education_cert_relevance_score": education_enabled,
    }
    enabled_total = sum(
        weight for component, weight in COMPONENT_WEIGHTS.items() if enabled[component]
    )
    component_weights = [
        ComponentWeight(
            component=component,
            configured_weight=weight,
            enabled=enabled[component],
            effective_weight=(weight / enabled_total if enabled_total else 0.0),
        )
        for component, weight in COMPONENT_WEIGHTS.items()
    ]
    return (
        ScoreBreakdown(
            required_skill_score=_group_score(matches, "required"),
            preferred_skill_score=_group_score(matches, "preferred"),
            unknown_skill_score=_group_score(matches, "unknown"),
            skill_coverage_score=skill_score,
            experience_relevance_score=round(experience_score, 2),
            project_relevance_score=round(project_score, 2),
            education_cert_relevance_score=round(education_score, 2),
            component_weights=component_weights,
        ),
        weight_sources,
    )


def calculate_fit_score(score_breakdown: ScoreBreakdown) -> float:
    scores = {
        "skill_coverage_score": score_breakdown.skill_coverage_score,
        "experience_relevance_score": score_breakdown.experience_relevance_score,
        "project_relevance_score": score_breakdown.project_relevance_score,
        "education_cert_relevance_score": score_breakdown.education_cert_relevance_score,
    }
    if not score_breakdown.component_weights:
        return round(score_breakdown.required_skill_score, 2)
    return round(
        sum(
            scores[item.component] * item.effective_weight
            for item in score_breakdown.component_weights
            if item.enabled
        ),
        2,
    )


def apply_fit_guardrails(
    raw_score: float,
    requirements: list[JDSkillRequirement],
    matches: list[SkillMatch],
    required_skill_score: float,
) -> tuple[float, list[ScoreAdjustment]]:
    score = raw_score
    adjustments: list[ScoreAdjustment] = []
    match_lookup = {match.jd_skill.lower(): match for match in matches}
    critical_missing = [
        requirement.skill
        for requirement in requirements
        if requirement.classification == "required"
        and requirement.critical
        and match_lookup[requirement.skill.lower()].match_level == "missing"
    ]
    if critical_missing and score >= 75:
        adjusted = 74.99
        adjustments.append(
            ScoreAdjustment(
                rule="CRITICAL_REQUIRED_SKILL_MISSING",
                reason=f"Missing critical JD skills: {', '.join(critical_missing)}.",
                score_before=score,
                score_after=adjusted,
            )
        )
        score = adjusted

    has_required = any(item.classification == "required" for item in requirements)
    if has_required and required_skill_score < 50 and score >= 50:
        adjusted = 49.99
        adjustments.append(
            ScoreAdjustment(
                rule="LOW_REQUIRED_SKILL_COVERAGE",
                reason="Required-skill evidence is below 50%.",
                score_before=score,
                score_after=adjusted,
            )
        )
        score = adjusted
    elif has_required and required_skill_score < 75 and score >= 75:
        adjusted = 74.99
        adjustments.append(
            ScoreAdjustment(
                rule="MEDIUM_REQUIRED_SKILL_COVERAGE",
                reason="Required-skill evidence is below 75%.",
                score_before=score,
                score_after=adjusted,
            )
        )
        score = adjusted
    return round(score, 2), adjustments


def evaluate_fit_level(fit_score: float, missing_required_count: int = 0) -> str:
    if fit_score >= 75:
        return "high"
    if fit_score >= 50:
        return "medium"
    return "low"
