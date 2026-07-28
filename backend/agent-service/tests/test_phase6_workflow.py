from app.core.config import Settings
from app.schemas.analysis import (
    AgentAnalyzeRequest,
    ParsedCV,
    ParsedJD,
)
from app.services.gemini import GeminiResult
from app.services.similarity import LexicalSimilarityProvider
from app.services.workflow import WorkflowServices, build_analysis_graph


class FakeGeminiService:
    enabled = True
    cv_parse_count = 0
    jd_parse_count = 0
    generation_count = 0

    def parse_cv(self, text: str) -> GeminiResult:
        self.cv_parse_count += 1
        return GeminiResult(
            value=ParsedCV(
                skills=["Python"],
                experience_summary="Built Python APIs with measurable outcomes.",
                experience_evidence=["Built Python APIs and reduced latency by 20%."],
            )
        )

    def parse_jd(self, text: str) -> GeminiResult:
        self.jd_parse_count += 1
        return GeminiResult(
            value=ParsedJD(
                job_title="AI Engineer",
                required_skills=["Python"],
                skill_requirements=[
                    {
                        "skill": "Python",
                        "classification": "required",
                        "critical": True,
                        "evidence": "Python is required.",
                        "base_weight": 1.0,
                    }
                ],
            )
        )

    def generate(self, prompt: str) -> GeminiResult:
        self.generation_count += 1
        return GeminiResult(value="Generated truthful cover letter.")


def settings() -> Settings:
    return Settings(
        _env_file=None,
        gemini_enabled=False,
    )


def test_workflow_accepts_mocked_gemini_structured_output_and_generation():
    gemini = FakeGeminiService()
    graph = build_analysis_graph(
        WorkflowServices(
            settings=settings(),
            gemini=gemini,
            similarity=LexicalSimilarityProvider(),
        )
    )
    state = graph.invoke(
        {
            "request": AgentAnalyzeRequest(
                cv_text="Python engineer who built APIs and reduced service latency by twenty percent.",
                jd_text="AI Engineer role where Python is required for building production AI services.",
            ),
            "warnings": [],
        }
    )

    assert state["parsed_jd"].job_title == "AI Engineer"
    assert state["fit_level"] == "high"
    assert state["cover_letter"] == "Generated truthful cover letter."
    assert gemini.cv_parse_count == 1
    assert gemini.jd_parse_count == 1
    assert gemini.generation_count == 1
