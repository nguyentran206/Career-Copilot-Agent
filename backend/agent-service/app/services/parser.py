import re

from app.services.language import detect_language


SKILL_PATTERNS = {
    "Python": ["python"],
    "SQL": ["sql", "structured query language"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Excel": ["excel", "microsoft excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django"],
    "Flask": ["flask"],
    "REST API": ["rest api", "restful api", "api development", "backend api"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Git": ["git", "github", "gitlab"],
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

PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "good to have",
    "a plus",
    "plus",
    "advantage",
    "bonus",
)
REQUIRED_MARKERS = (
    "required",
    "must",
    "mandatory",
    "need",
    "needs",
    "looking for",
    "proficiency",
    "strong knowledge",
    "experience with",
)
CRITICAL_MARKERS = ("must", "mandatory", "non-negotiable", "required")

JOB_TITLE_PATTERNS = (
    "data scientist",
    "data analyst",
    "business analyst",
    "backend engineer",
    "backend developer",
    "software engineer",
    "software developer",
    "machine learning engineer",
    "ai engineer",
    "devops engineer",
    "frontend developer",
    "full stack developer",
)


def normalize_text_for_matching(text: str) -> str:
    lower_text = text.lower()
    normalized = re.sub(r"[^a-z0-9+#.]+", " ", lower_text)
    compacted = re.sub(r"\s+", " ", normalized).strip()
    return f" {compacted} "


def contains_phrase(normalized_text: str, phrase: str) -> bool:
    normalized_phrase = normalize_text_for_matching(phrase).strip()
    return f" {normalized_phrase} " in normalized_text


def split_sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?;])\s+|[\r\n]+", text)
        if sentence.strip()
    ]


def extract_known_skills(text: str) -> list[str]:
    normalized_text = normalize_text_for_matching(text)
    skills = []

    for canonical_skill, patterns in SKILL_PATTERNS.items():
        if any(contains_phrase(normalized_text, pattern) for pattern in patterns):
            skills.append(canonical_skill)

    return sorted(set(skills))


def find_skill_evidence(skill: str, text: str) -> str | None:
    patterns = SKILL_PATTERNS.get(skill, [skill])
    for sentence in split_sentences(text):
        normalized = normalize_text_for_matching(sentence)
        if any(contains_phrase(normalized, pattern) for pattern in patterns):
            return sentence
    return None


def classify_skill_requirement(evidence: str | None) -> tuple[str, bool]:
    normalized = (evidence or "").lower()
    if any(marker in normalized for marker in PREFERRED_MARKERS):
        return "preferred", False
    if any(marker in normalized for marker in REQUIRED_MARKERS):
        return "required", any(marker in normalized for marker in CRITICAL_MARKERS)
    return "unknown", False


def get_base_weight(classification: str) -> float:
    return {"required": 1.0, "preferred": 0.65, "unknown": 0.45}[classification]


def detect_job_title(text: str) -> str | None:
    normalized = normalize_text_for_matching(text)
    for title in JOB_TITLE_PATTERNS:
        if contains_phrase(normalized, title):
            return title.title()
    return None


def parse_cv_text(cv_text: str) -> dict:
    language_info = detect_language(cv_text)
    sentences = split_sentences(cv_text)
    projects = [sentence for sentence in sentences if "project" in sentence.lower()]
    experience = [
        sentence
        for sentence in sentences
        if any(
            marker in sentence.lower()
            for marker in ("experience", "worked", "built", "developed", "implemented", "created")
        )
    ]
    education = [
        sentence
        for sentence in sentences
        if any(marker in sentence.lower() for marker in ("degree", "bachelor", "master", "university"))
    ]
    certifications = [
        sentence
        for sentence in sentences
        if any(marker in sentence.lower() for marker in ("certified", "certification", "certificate"))
    ]

    return {
        "language_info": language_info,
        "skills": extract_known_skills(cv_text),
        "experience_summary": " ".join(experience[:3]) or None,
        "experience_evidence": experience,
        "projects": projects,
        "education": education,
        "certifications": certifications,
        "localized_evidence": [
            {
                "original_text": sentence,
                "source_language": language_info.primary_language,
                "english_text": sentence if language_info.primary_language == "en" else None,
            }
            for sentence in dict.fromkeys(experience + projects + education + certifications)
        ],
    }


def parse_jd_text(jd_text: str) -> dict:
    language_info = detect_language(jd_text)
    skills = extract_known_skills(jd_text)
    requirements = []

    for skill in skills:
        evidence = find_skill_evidence(skill, jd_text)
        classification, critical = classify_skill_requirement(evidence)
        requirements.append(
            {
                "skill": skill,
                "classification": classification,
                "critical": critical,
                "evidence": evidence,
                "original_evidence": evidence,
                "english_evidence": (
                    evidence if language_info.primary_language == "en" else None
                ),
                "base_weight": get_base_weight(classification),
            }
        )

    sentences = split_sentences(jd_text)
    responsibilities = [
        sentence
        for sentence in sentences
        if any(
            marker in sentence.lower()
            for marker in ("responsible", "build", "develop", "design", "analyze", "maintain", "work with")
        )
    ]
    experience_requirements = [
        sentence
        for sentence in sentences
        if any(marker in sentence.lower() for marker in ("years", "experience", "senior", "junior"))
    ]
    project_requirements = [
        sentence
        for sentence in sentences
        if any(marker in sentence.lower() for marker in ("project", "portfolio"))
    ]
    education_requirements = [
        sentence
        for sentence in sentences
        if any(
            marker in sentence.lower()
            for marker in ("degree", "bachelor", "master", "certification", "certified")
        )
    ]

    return {
        "language_info": language_info,
        "required_skills": [
            item["skill"] for item in requirements if item["classification"] == "required"
        ],
        "preferred_skills": [
            item["skill"] for item in requirements if item["classification"] == "preferred"
        ],
        "unknown_skills": [
            item["skill"] for item in requirements if item["classification"] == "unknown"
        ],
        "skill_requirements": requirements,
        "job_title": detect_job_title(jd_text),
        "responsibilities": responsibilities,
        "experience_requirements": experience_requirements,
        "project_requirements": project_requirements,
        "education_requirements": education_requirements,
        "domain_keywords": [],
    }
