from app.schemas.analysis import CVEvidence, JDSkillRequirement, ParsedCV, SkillMatch
from app.services.parser import find_skill_evidence
from app.services.similarity import SimilarityProvider


# Only relationships that can partially satisfy the same capability belong here.
# Supporting technologies such as Python -> Machine Learning or LangChain ->
# LangGraph are deliberately excluded.
TAXONOMY_EQUIVALENTS: dict[str, dict[str, float]] = {
    "PostgreSQL": {"SQL": 0.82},
    "SQL": {"PostgreSQL": 0.82},
    "REST API": {"FastAPI": 0.75, "Django": 0.72, "Flask": 0.72},
    "FastAPI": {"REST API": 0.75},
    "Dashboard": {"Power BI": 0.78, "Tableau": 0.78},
}

RELATED_NOT_EQUIVALENT = {
    frozenset(("LangGraph", "LangChain")),
    frozenset(("Power BI", "Tableau")),
    frozenset(("Machine Learning", "Python")),
    frozenset(("RAG", "LLM")),
}


def get_match_level(similarity: float, strong: float, partial: float) -> str:
    if similarity >= strong:
        return "strong"
    if similarity >= partial:
        return "partial"
    return "missing"


def evidence_strength(sentence: str, source: str) -> float:
    normalized = sentence.lower()
    measurable = any(character.isdigit() for character in sentence) or any(
        marker in normalized for marker in ("increased", "reduced", "improved", "saved")
    )
    if source == "experience" and measurable:
        return 1.0
    if source == "experience":
        return 0.90
    if source == "project":
        return 0.85
    if source == "skills":
        return 0.70
    return 0.55


def collect_skill_evidence(skill: str, parsed_cv: ParsedCV, cv_text: str) -> list[CVEvidence]:
    evidence: list[CVEvidence] = []
    localized_lookup = {
        item.english_text: item
        for item in parsed_cv.localized_evidence
        if item.english_text
    }
    for sentence in parsed_cv.experience_evidence:
        if find_skill_evidence(skill, sentence):
            evidence.append(
                CVEvidence(
                    source="experience",
                    text=sentence,
                    strength=evidence_strength(sentence, "experience"),
                    source_language=localized_lookup.get(sentence).source_language
                    if sentence in localized_lookup
                    else parsed_cv.language_info.primary_language,
                    original_text=localized_lookup.get(sentence).original_text
                    if sentence in localized_lookup
                    else None,
                )
            )
    for sentence in parsed_cv.projects:
        if find_skill_evidence(skill, sentence):
            evidence.append(
                CVEvidence(
                    source="project",
                    text=sentence,
                    strength=evidence_strength(sentence, "project"),
                    source_language=localized_lookup.get(sentence).source_language
                    if sentence in localized_lookup
                    else parsed_cv.language_info.primary_language,
                    original_text=localized_lookup.get(sentence).original_text
                    if sentence in localized_lookup
                    else None,
                )
            )

    if skill in parsed_cv.skills and not evidence:
        sentence = (
            find_skill_evidence(skill, cv_text)
            if parsed_cv.language_info.primary_language == "en"
            else None
        ) or skill
        source = "skills" if "skill" in sentence.lower() else "mention"
        evidence.append(
            CVEvidence(
                source=source,
                text=sentence,
                strength=evidence_strength(sentence, source),
                source_language=parsed_cv.language_info.primary_language,
            )
        )
    return evidence


def find_best_skill_match(
    jd_skill: str,
    cv_skills: list[str],
    similarity_provider: SimilarityProvider,
    strong_threshold: float,
    partial_threshold: float,
) -> tuple[str | None, float, str]:
    cv_skill_lookup = {skill.lower(): skill for skill in cv_skills}
    exact_match = cv_skill_lookup.get(jd_skill.lower())
    if exact_match:
        return exact_match, 1.0, "exact"

    taxonomy_matches = TAXONOMY_EQUIVALENTS.get(jd_skill, {})
    taxonomy_candidates = [
        (cv_skill, taxonomy_matches[cv_skill])
        for cv_skill in cv_skills
        if cv_skill in taxonomy_matches
    ]
    if taxonomy_candidates:
        matched_skill, score = max(taxonomy_candidates, key=lambda item: item[1])
        return matched_skill, score, "taxonomy"

    semantic_candidates = [
        (cv_skill, similarity_provider.similarity(jd_skill, cv_skill))
        for cv_skill in cv_skills
        if frozenset((jd_skill, cv_skill)) not in RELATED_NOT_EQUIVALENT
    ]
    if semantic_candidates:
        matched_skill, score = max(semantic_candidates, key=lambda item: item[1])
        if score >= partial_threshold:
            return matched_skill, score, "semantic"

    return None, 0.0, "none"


def match_skills(
    requirements: list[JDSkillRequirement],
    parsed_cv: ParsedCV,
    cv_text: str,
    similarity_provider: SimilarityProvider,
    strong_threshold: float,
    partial_threshold: float,
) -> list[SkillMatch]:
    matches: list[SkillMatch] = []
    for requirement in requirements:
        resume_skill, similarity, match_type = find_best_skill_match(
            jd_skill=requirement.skill,
            cv_skills=parsed_cv.skills,
            similarity_provider=similarity_provider,
            strong_threshold=strong_threshold,
            partial_threshold=partial_threshold,
        )
        evidence = (
            collect_skill_evidence(resume_skill, parsed_cv, cv_text)
            if resume_skill
            else []
        )
        strongest_evidence = max(
            (item.strength for item in evidence),
            default=0.0,
        )
        evidence_bonus = min(0.10, max(0, len(evidence) - 1) * 0.05)
        evidence_score = min(1.0, similarity * (strongest_evidence + evidence_bonus))

        matches.append(
            SkillMatch(
                jd_skill=requirement.skill,
                resume_skill=resume_skill,
                similarity=round(similarity, 4),
                match_level=get_match_level(
                    similarity,
                    strong=strong_threshold,
                    partial=partial_threshold,
                ),
                importance=requirement.base_weight,
                classification=requirement.classification,
                match_type=match_type,
                evidence=evidence,
                evidence_score=round(evidence_score, 4),
            )
        )
    return matches


def match_required_skills(
    required_skills: list[str],
    cv_skills: list[str],
) -> list[SkillMatch]:
    """Backward-compatible deterministic helper used by older callers/tests."""
    from app.services.similarity import LexicalSimilarityProvider

    requirements = [
        JDSkillRequirement(
            skill=skill,
            classification="required",
            base_weight=1.0,
        )
        for skill in required_skills
    ]
    parsed_cv = ParsedCV(skills=cv_skills)
    return match_skills(
        requirements=requirements,
        parsed_cv=parsed_cv,
        cv_text=" ".join(cv_skills),
        similarity_provider=LexicalSimilarityProvider(),
        strong_threshold=0.85,
        partial_threshold=0.70,
    )
