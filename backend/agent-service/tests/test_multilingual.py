from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.schemas.analysis import AgentAnalyzeRequest, ParsedCV, ParsedJD
from app.services.gemini import GeminiResult
from app.services.language import detect_language, needs_english_canonicalization
from app.services.similarity import LexicalSimilarityProvider
from app.services.workflow import WorkflowServices, build_analysis_graph


client = TestClient(app)


class MultilingualGeminiFixture:
    enabled = True

    def parse_cv(self, text: str) -> GeminiResult:
        return GeminiResult(
            value=ParsedCV(
                language_info={
                    "primary_language": "vi",
                    "detected_languages": ["vi", "en"],
                    "is_mixed_language": True,
                    "confidence": 0.95,
                },
                skills=["Python"],
                experience_summary="Built backend APIs with Python.",
                experience_evidence=["Built backend APIs with Python and reduced latency by 30%."],
                projects=["Built an internal AI service project with Python."],
                localized_evidence=[
                    {
                        "original_text": "Xây dựng API backend bằng Python và giảm 30% độ trễ.",
                        "source_language": "vi",
                        "english_text": "Built backend APIs with Python and reduced latency by 30%.",
                    }
                ],
            )
        )

    def parse_jd(self, text: str) -> GeminiResult:
        return GeminiResult(
            value=ParsedJD(
                language_info={
                    "primary_language": "vi",
                    "detected_languages": ["vi"],
                    "is_mixed_language": False,
                    "confidence": 0.98,
                },
                job_title="AI Engineer",
                project_requirements=["Build production AI service projects."],
                required_skills=["Python"],
                skill_requirements=[
                    {
                        "skill": "Python",
                        "classification": "required",
                        "critical": True,
                        "evidence": "Python experience is mandatory.",
                        "original_evidence": "Bắt buộc có kinh nghiệm Python.",
                        "english_evidence": "Python experience is mandatory.",
                        "base_weight": 1.0,
                    }
                ],
            )
        )

    def generate(self, prompt: str) -> GeminiResult:
        return GeminiResult(value="English-only generated cover letter.")


def test_language_detection_handles_english_vietnamese_and_mixed_text():
    assert detect_language("Backend engineer with Python experience and project work.").primary_language == "en"
    assert detect_language("Có kinh nghiệm phát triển hệ thống bằng Python.").primary_language == "vi"
    assert detect_language("Có kinh nghiệm Python and backend project work.").is_mixed_language
    spanish = detect_language(
        "Experiencia desarrollando servicios de datos y aplicaciones para clientes internacionales."
    )
    assert spanish.primary_language == "es"
    assert needs_english_canonicalization(spanish)


def test_non_english_input_without_gemini_uses_safe_low_confidence_fallback():
    response = client.post(
        "/api/v1/analyze",
        json={
            "cv_text": "Ứng viên có kinh nghiệm sử dụng Python để xây dựng dịch vụ backend nội bộ.",
            "jd_text": "Vị trí kỹ sư AI bắt buộc có kinh nghiệm Python để phát triển các dịch vụ sản xuất.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "MULTILINGUAL_NORMALIZATION_UNAVAILABLE" in data["analysis_warnings"]
    assert data["score_confidence"] <= 0.40
    assert data["parsed_jd"]["skill_requirements"][0]["classification"] == "unknown"
    assert data["parsed_jd"]["skill_requirements"][0]["evidence"] is None
    assert data["skill_matches"][0]["evidence"][0]["text"] == "Python"
    assert "original_text" not in data["skill_matches"][0]["evidence"][0]


def test_mocked_gemini_canonicalizes_multilingual_input_to_english():
    graph = build_analysis_graph(
        WorkflowServices(
            settings=Settings(_env_file=None),
            gemini=MultilingualGeminiFixture(),
            similarity=LexicalSimilarityProvider(),
        )
    )
    state = graph.invoke(
        {
            "request": AgentAnalyzeRequest(
                cv_text="Xây dựng API backend bằng Python và giảm 30% độ trễ cho hệ thống nội bộ.",
                jd_text="Vị trí AI Engineer bắt buộc có kinh nghiệm Python để phát triển dịch vụ AI.",
            ),
            "warnings": [],
            "multilingual_fallback": False,
        }
    )

    assert state["parsed_cv"].experience_evidence[0].startswith("Built backend APIs")
    assert state["parsed_jd"].skill_requirements[0].evidence == "Python experience is mandatory."
    assert state["score_confidence"] > 0.40
    assert state["cover_letter"] == "English-only generated cover letter."
    project_weight = next(
        item
        for item in state["score_breakdown"].component_weights
        if item.component == "project_relevance_score"
    )
    assert project_weight.enabled
