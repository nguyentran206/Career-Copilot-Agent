import re


SKILL_PATTERNS = {
    "Python": ["python"],
    "SQL": ["sql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Excel": ["excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django"],
    "Flask": ["flask"],
    "REST API": ["rest api", "restful api", "api development", "backend api"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "Machine Learning": ["machine learning", "ml"],
    "Generative AI": ["generative ai", "gen ai", "genai"],
    "LLM": ["llm", "large language model", "large language models"],
    "RAG": ["rag", "retrieval augmented generation"],
    "LangChain": ["langchain", "lang chain"],
    "LangGraph": ["langgraph", "lang graph"],
    "Embedding": ["embedding", "embeddings", "vector search", "semantic search"],
    "Data Analysis": ["data analysis", "data analyst", "analytics"],
    "Dashboard": ["dashboard", "dashboards"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy", "num py"],
    "Statistics": ["statistics", "statistical analysis"],
}


def normalize_text_for_matching(text: str) -> str:
    lower_text = text.lower()
    normalized = re.sub(r"[^a-z0-9+#.]+", " ", lower_text)
    compacted = re.sub(r"\s+", " ", normalized).strip()
    return f" {compacted} "


def contains_phrase(normalized_text: str, phrase: str) -> bool:
    normalized_phrase = normalize_text_for_matching(phrase).strip()
    return f" {normalized_phrase} " in normalized_text


def extract_known_skills(text: str) -> list[str]:
    normalized_text = normalize_text_for_matching(text)
    skills = []

    for canonical_skill, patterns in SKILL_PATTERNS.items():
        if any(contains_phrase(normalized_text, pattern) for pattern in patterns):
            skills.append(canonical_skill)

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
