from app.schemas.analysis import (
    JDSkillRequirement,
    SkillMatch,
)
from app.services.matcher import find_best_skill_match
from app.services.parser import parse_jd_text
from app.services.scorer import (
    apply_fit_guardrails,
    calculate_skill_coverage,
)
from app.services.similarity import LexicalSimilarityProvider


def requirement(
    skill: str,
    classification: str,
    base_weight: float,
    critical: bool = False,
) -> JDSkillRequirement:
    return JDSkillRequirement(
        skill=skill,
        classification=classification,
        critical=critical,
        base_weight=base_weight,
    )


def match(
    skill: str,
    classification: str,
    evidence_score: float,
    match_level: str = "strong",
) -> SkillMatch:
    return SkillMatch(
        jd_skill=skill,
        resume_skill=skill if match_level != "missing" else None,
        similarity=evidence_score if match_level != "missing" else 0,
        match_level=match_level,
        match_type="exact" if match_level != "missing" else "none",
        classification=classification,
        evidence_score=evidence_score,
    )


def test_jd_parser_classifies_required_preferred_and_unknown_skills():
    parsed = parse_jd_text(
        "Python is required. Power BI is preferred. The team also uses SQL "
        "for reporting and business analysis workflows."
    )

    assert parsed["required_skills"] == ["Python"]
    assert parsed["preferred_skills"] == ["Power BI"]
    assert parsed["unknown_skills"] == ["SQL"]


def test_skill_coverage_uses_jd_classification_weights_only():
    requirements = [
        requirement("Python", "required", 1.0),
        requirement("SQL", "unknown", 0.45),
    ]
    matches = [
        match("Python", "required", 1.0),
        match("SQL", "unknown", 0.0, match_level="missing"),
    ]

    score, sources = calculate_skill_coverage(requirements, matches)

    assert score == 68.97
    assert [source.final_weight for source in sources] == [1.0, 0.45]


def test_missing_critical_required_skill_caps_high_score():
    requirements = [requirement("Python", "required", 1.0, critical=True)]
    matches = [match("Python", "required", 0.0, match_level="missing")]

    score, adjustments = apply_fit_guardrails(
        raw_score=90,
        requirements=requirements,
        matches=matches,
        required_skill_score=0,
    )

    assert score == 49.99
    assert [item.rule for item in adjustments] == [
        "CRITICAL_REQUIRED_SKILL_MISSING",
        "LOW_REQUIRED_SKILL_COVERAGE",
    ]


def test_related_skill_does_not_substitute_for_explicit_requirement():
    matched_skill, similarity, match_type = find_best_skill_match(
        jd_skill="LangGraph",
        cv_skills=["LangChain"],
        similarity_provider=LexicalSimilarityProvider(),
        strong_threshold=0.85,
        partial_threshold=0.70,
    )

    assert matched_skill is None
    assert similarity == 0
    assert match_type == "none"
