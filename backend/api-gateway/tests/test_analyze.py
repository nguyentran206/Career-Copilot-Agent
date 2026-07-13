import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.analyze.schemas import AnalysisResultPayload
from app.modules.session.schemas import SessionError
from app.modules.session.store import clear_sessions, mark_session_completed, mark_session_failed


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_session_store():
    clear_sessions()
    yield
    clear_sessions()


def build_analysis_result() -> AnalysisResultPayload:
    return AnalysisResultPayload(
        cv_parse_result={
            "filename": "cv.pdf",
            "document_type": "cv",
            "content_type": "application/pdf",
            "file_size_bytes": 12345,
            "page_count": 1,
            "text_length": 84,
            "warnings": [],
        },
        analysis_result={
            "fit_score": 100,
            "fit_level": "high",
            "score_breakdown": {
                "required_skill_score": 100,
                "preferred_skill_score": 0,
                "experience_relevance_score": 0,
                "project_domain_relevance_score": 0,
                "education_cert_tool_score": 0,
            },
            "parsed_cv": {
                "skills": ["FastAPI", "Python"],
                "experience_summary": None,
                "projects": [],
                "education": [],
                "certifications": [],
            },
            "parsed_jd": {
                "required_skills": ["FastAPI", "Python"],
                "preferred_skills": [],
                "responsibilities": [],
                "domain_keywords": [],
            },
            "skill_matches": [
                {
                    "jd_skill": "Python",
                    "resume_skill": "Python",
                    "similarity": 1.0,
                    "match_level": "strong",
                    "importance": 1.0,
                }
            ],
            "matched_skills": ["Python"],
            "missing_skills": [],
            "cv_improvement_suggestions": [],
            "cover_letter": "Cover letter generation will be implemented in a later phase.",
            "learning_roadmap": None,
        },
    )


def post_analyze(jd_text: str, file_content: bytes = b"fake pdf content"):
    files = {
        "cv_file": ("cv.pdf", file_content, "application/pdf")
    }

    return client.post(
        "/api/v1/analyze",
        files=files,
        data={
            "jd_text": jd_text
        },
    )


def test_analyze_without_cv_file():
    response = client.post(
        "/api/v1/analyze",
        data={"jd_text": "We are looking for a Python developer."},
    )

    assert response.status_code == 422


def test_analyze_without_jd_text():
    files = {
        "cv_file": ("cv.pdf", b"fake pdf content", "application/pdf")
    }

    response = client.post(
        "/api/v1/analyze",
        files=files,
    )

    assert response.status_code == 422


def test_analyze_with_blank_jd_text():
    response = post_analyze("     ")

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JD_TEXT_REQUIRED"


def test_analyze_with_too_short_jd_text():
    response = post_analyze("Python")

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JD_TEXT_TOO_SHORT"


def test_analyze_with_empty_cv_file():
    response = post_analyze(
        jd_text="We are looking for a Python developer with FastAPI experience.",
        file_content=b"",
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPTY_CV_FILE"


def test_analyze_starts_processing_session(monkeypatch):
    async def fake_background_task(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.modules.analyze.routes.run_analysis_session",
        fake_background_task,
    )

    response = post_analyze(
        "We are looking for a Python developer with FastAPI experience and backend API development skills."
    )

    assert response.status_code == 202

    data = response.json()
    assert data["session_id"]
    assert data["status"] == "processing"

    session_response = client.get(f"/api/v1/session/{data['session_id']}")
    assert session_response.status_code == 200
    assert session_response.json()["status"] == "processing"
    assert session_response.json()["result"] is None
    assert session_response.json()["error"] is None


def test_session_completed_after_background_task(monkeypatch):
    async def fake_background_task(session_id: str, *args, **kwargs):
        mark_session_completed(
            session_id=session_id,
            result=build_analysis_result(),
        )

    monkeypatch.setattr(
        "app.modules.analyze.routes.run_analysis_session",
        fake_background_task,
    )

    response = post_analyze(
        "We are looking for a Python developer with FastAPI experience and backend API development skills."
    )

    assert response.status_code == 202
    session_id = response.json()["session_id"]

    session_response = client.get(f"/api/v1/session/{session_id}")
    assert session_response.status_code == 200

    data = session_response.json()
    assert data["session_id"] == session_id
    assert data["status"] == "completed"
    assert data["result"]["analysis_result"]["fit_score"] == 100
    assert data["error"] is None


def test_session_failed_after_background_task(monkeypatch):
    async def fake_background_task(session_id: str, *args, **kwargs):
        mark_session_failed(
            session_id=session_id,
            error=SessionError(
                code="AGENT_SERVICE_UNAVAILABLE",
                message="Agent Service is unavailable.",
                detail=None,
            ),
        )

    monkeypatch.setattr(
        "app.modules.analyze.routes.run_analysis_session",
        fake_background_task,
    )

    response = post_analyze(
        "We are looking for a Python developer with FastAPI experience and backend API development skills."
    )

    assert response.status_code == 202
    session_id = response.json()["session_id"]

    session_response = client.get(f"/api/v1/session/{session_id}")
    assert session_response.status_code == 200

    data = session_response.json()
    assert data["status"] == "failed"
    assert data["result"] is None
    assert data["error"]["code"] == "AGENT_SERVICE_UNAVAILABLE"


def test_unknown_session_returns_404():
    response = client.get("/api/v1/session/unknown-session-id")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SESSION_NOT_FOUND"
