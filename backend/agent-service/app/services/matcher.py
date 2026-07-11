from app.schemas.analysis import SkillMatch


RELATED_SKILL_MATCHES = {
    "PostgreSQL": {"SQL"},
    "SQL": {"PostgreSQL"},
    "REST API": {"FastAPI", "Django", "Flask"},
    "FastAPI": {"REST API"},
    "Django": {"REST API"},
    "Flask": {"REST API"},
    "Machine Learning": {"Python", "Statistics", "NumPy", "Pandas"},
    "Data Analysis": {"SQL", "Excel", "Pandas", "Statistics", "Dashboard"},
    "Dashboard": {"Power BI", "Tableau"},
    "Embedding": {"RAG", "LLM"},
    "RAG": {"LLM", "Embedding"},
    "Generative AI": {"LLM", "RAG"},
    "LangGraph": {"LangChain", "LLM"},
    "LangChain": {"LangGraph", "LLM"},
}


def get_match_level(similarity: float) -> str:
    if similarity >= 0.80:
        return "strong"
    if similarity >= 0.65:
        return "partial"
    return "missing"


def find_best_skill_match(
    required_skill: str,
    cv_skills: list[str],
) -> tuple[str | None, float]:
    cv_skill_lookup = {skill.lower(): skill for skill in cv_skills}

    exact_match = cv_skill_lookup.get(required_skill.lower())
    if exact_match:
        return exact_match, 1.0

    related_skills = RELATED_SKILL_MATCHES.get(required_skill, set())
    for cv_skill in cv_skills:
        if cv_skill in related_skills:
            return cv_skill, 0.70

    return None, 0.0


def match_required_skills(
    required_skills: list[str],
    cv_skills: list[str],
) -> list[SkillMatch]:
    matches: list[SkillMatch] = []

    for required_skill in required_skills:
        matched_skill, similarity = find_best_skill_match(
            required_skill=required_skill,
            cv_skills=cv_skills,
        )

        matches.append(
            SkillMatch(
                jd_skill=required_skill,
                resume_skill=matched_skill,
                similarity=similarity,
                match_level=get_match_level(similarity),
                importance=1.0,
            )
        )

    return matches
