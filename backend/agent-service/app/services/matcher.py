from app.schemas.analysis import SkillMatch


def get_match_level(similarity: float) -> str:
    if similarity >= 0.80:
        return "strong"
    if similarity >= 0.65:
        return "partial"
    return "missing"


def match_required_skills(
    required_skills: list[str],
    cv_skills: list[str],
) -> list[SkillMatch]:
    cv_skill_lookup = {skill.lower(): skill for skill in cv_skills}
    matches: list[SkillMatch] = []

    for required_skill in required_skills:
        matched_skill = cv_skill_lookup.get(required_skill.lower())
        similarity = 1.0 if matched_skill else 0.0

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