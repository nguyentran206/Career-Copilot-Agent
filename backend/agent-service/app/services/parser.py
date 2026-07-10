COMMON_SKILLS = [
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "fastapi",
    "docker",
    "aws",
    "machine learning",
    "data analysis",
    "dashboard",
    "pandas",
    "numpy",
    "statistics",
]


def extract_known_skills(text: str) -> list[str]:
    lower_text = text.lower()
    skills = []

    for skill in COMMON_SKILLS:
        if skill in lower_text:
            skills.append(skill.title())

    return sorted(set(skills))


def parse_cv_text(cv_text: str) -> dict:
    return {
        "skills": extract_known_skills(cv_text),
        "experience_summary": None,
        "projects": [],
        "education": [],
        "certifications": [],
    }


def parse_jd_text(jd_text: str) -> dict:
    skills = extract_known_skills(jd_text)

    return {
        "required_skills": skills,
        "preferred_skills": [],
        "responsibilities": [],
        "domain_keywords": [],
    }