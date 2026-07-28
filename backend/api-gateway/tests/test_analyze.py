import asyncio

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.core.request_limits import analyze_request_limiter
from app.modules.analyze.schemas import (
    AnalysisResultPayload,
    DocumentParserResponse,
)
from app.modules.analyze.service import (
    analyze_cv_with_agent_service,
    parse_document_bytes_with_document_parser,
    parse_cv_bytes_with_document_parser,
    run_analysis,
)
from app.modules.session.schemas import SessionError
from app.modules.session.store import clear_sessions, mark_session_completed, mark_session_failed


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_session_store():
    clear_sessions()
    analyze_request_limiter.clear()
    yield
    clear_sessions()
    analyze_request_limiter.clear()


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
                "project_relevance_score": 0,
                "education_cert_relevance_score": 0,
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

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JD_INPUT_REQUIRED"


def test_analyze_rejects_text_and_pdf_jd_together():
    response = client.post(
        "/api/v1/analyze",
        files={
            "cv_file": ("cv.pdf", b"fake cv", "application/pdf"),
            "jd_file": ("jd.pdf", b"fake jd", "application/pdf"),
        },
        data={"jd_text": "A sufficiently long Job Description using Python and FastAPI."},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JD_INPUT_CONFLICT"


def test_analyze_accepts_jd_pdf_and_passes_it_to_background_task(monkeypatch):
    captured = {}

    async def fake_background_task(*args, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        "app.modules.analyze.routes.run_analysis_session",
        fake_background_task,
    )
    response = client.post(
        "/api/v1/analyze",
        files={
            "cv_file": ("cv.pdf", b"fake cv", "application/pdf"),
            "jd_file": ("jd.pdf", b"fake jd", "application/pdf"),
        },
    )

    assert response.status_code == 202
    assert captured["jd_text"] is None
    assert captured["jd_filename"] == "jd.pdf"
    assert captured["jd_file_bytes"] == b"fake jd"


def test_analyze_rejects_non_pdf_jd_file():
    response = client.post(
        "/api/v1/analyze",
        files={
            "cv_file": ("cv.pdf", b"fake cv", "application/pdf"),
            "jd_file": ("jd.txt", b"fake jd", "text/plain"),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JD_FILE_NOT_PDF"


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
    assert response.headers["cache-control"].startswith("no-store")
    assert response.headers["x-request-id"]

    data = response.json()
    assert data["session_id"]
    assert data["status"] == "processing"

    session_response = client.get(f"/api/v1/session/{data['session_id']}")
    assert session_response.status_code == 200
    assert session_response.json()["status"] == "processing"
    assert session_response.json()["result"] is None
    assert session_response.json()["error"] is None
    assert session_response.json()["expires_at"]
    assert session_response.headers["cache-control"].startswith("no-store")


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


def test_analyze_rejects_when_concurrency_capacity_is_full(monkeypatch):
    monkeypatch.setattr("app.core.request_limits.settings.max_concurrent_analyses", 0)
    response = post_analyze(
        "We need a Python engineer with FastAPI experience building backend services."
    )

    assert response.status_code == 429
    assert response.json()["detail"]["code"] == "ANALYSIS_CAPACITY_REACHED"
    assert response.headers["retry-after"] == "5"


def test_analyze_returns_session_capacity_error(monkeypatch):
    monkeypatch.setattr("app.modules.session.store.settings.max_sessions", 0)
    response = post_analyze(
        "We need a Python engineer with FastAPI experience building backend services."
    )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "SESSION_CAPACITY_REACHED"
    assert response.headers["retry-after"] == "30"


def test_request_id_is_preserved_for_safe_caller_value():
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "frontend-test-123"},
    )

    assert response.headers["x-request-id"] == "frontend-test-123"


def test_document_parser_client_uses_parser_timeout(monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json():
            return {
                "filename": "cv.pdf",
                "document_type": "cv",
                "content_type": "application/pdf",
                "file_size_bytes": 16,
                "page_count": 1,
                "text": "Extracted CV text with enough content for downstream analysis.",
                "text_length": 62,
                "warnings": [],
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, files, data, headers):
            captured["request_id"] = headers["X-Request-ID"]
            captured["document_type"] = data["document_type"]
            return FakeResponse()

    monkeypatch.setattr(
        "app.modules.analyze.service.httpx.AsyncClient",
        FakeAsyncClient,
    )

    asyncio.run(
        parse_cv_bytes_with_document_parser(
            filename="cv.pdf",
            content_type="application/pdf",
            file_bytes=b"fake pdf content",
        )
    )

    assert captured["timeout"].connect == 5.0
    assert captured["timeout"].read == 30.0
    assert captured["request_id"]
    assert captured["document_type"] == "cv"


def test_document_parser_client_marks_jd_document_type(monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json():
            return {
                "filename": "jd.pdf",
                "document_type": "jd",
                "content_type": "application/pdf",
                "file_size_bytes": 16,
                "page_count": 1,
                "text": "A Job Description with Python and FastAPI requirements for backend services.",
                "text_length": 76,
                "warnings": [],
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, files, data, headers):
            captured["document_type"] = data["document_type"]
            return FakeResponse()

    monkeypatch.setattr("app.modules.analyze.service.httpx.AsyncClient", FakeAsyncClient)
    result = asyncio.run(
        parse_document_bytes_with_document_parser(
            filename="jd.pdf",
            content_type="application/pdf",
            file_bytes=b"fake pdf content",
            document_type="jd",
        )
    )

    assert captured["document_type"] == "jd"
    assert result.document_type == "jd"


def test_run_analysis_uses_text_extracted_from_jd_pdf(monkeypatch):
    captured = {}

    async def fake_parse_cv(**kwargs):
        return DocumentParserResponse(
            filename="cv.pdf",
            document_type="cv",
            content_type="application/pdf",
            file_size_bytes=10,
            page_count=1,
            text="Candidate with Python and FastAPI experience building backend services.",
            text_length=70,
            warnings=[],
        )

    async def fake_parse_document(**kwargs):
        return DocumentParserResponse(
            filename="jd.pdf",
            document_type="jd",
            content_type="application/pdf",
            file_size_bytes=10,
            page_count=1,
            text="We need a Python engineer with FastAPI experience building backend services.",
            text_length=74,
            warnings=[],
        )

    async def fake_agent(**kwargs):
        captured["jd_text"] = kwargs["jd_text"]
        return build_analysis_result().analysis_result

    monkeypatch.setattr(
        "app.modules.analyze.service.parse_cv_bytes_with_document_parser",
        fake_parse_cv,
    )
    monkeypatch.setattr(
        "app.modules.analyze.service.parse_document_bytes_with_document_parser",
        fake_parse_document,
    )
    monkeypatch.setattr(
        "app.modules.analyze.service.analyze_cv_with_agent_service",
        fake_agent,
    )

    result = asyncio.run(
        run_analysis(
            filename="cv.pdf",
            content_type="application/pdf",
            file_bytes=b"fake cv",
            jd_text=None,
            jd_filename="jd.pdf",
            jd_content_type="application/pdf",
            jd_file_bytes=b"fake jd",
        )
    )

    assert captured["jd_text"].startswith("We need a Python engineer")
    assert result.jd_parse_result is not None
    assert result.jd_parse_result.document_type == "jd"


def test_agent_client_uses_agent_timeout(monkeypatch):
    captured = {}
    response_payload = build_analysis_result().analysis_result.model_dump(mode="json")

    class FakeResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json():
            return response_payload

    class FakeAsyncClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json, headers):
            captured["request_id"] = headers["X-Request-ID"]
            return FakeResponse()

    monkeypatch.setattr(
        "app.modules.analyze.service.httpx.AsyncClient",
        FakeAsyncClient,
    )

    asyncio.run(
        analyze_cv_with_agent_service(
            cv_text="Candidate has Python and FastAPI experience building backend services.",
            jd_text="We need a Python engineer with FastAPI experience building backend services.",
        )
    )

    assert captured["timeout"].connect == 5.0
    assert captured["timeout"].read == 150.0
    assert captured["request_id"]


@pytest.mark.parametrize(
    ("call", "expected_code"),
    [
        (
            lambda: parse_cv_bytes_with_document_parser(
                filename="cv.pdf",
                content_type="application/pdf",
                file_bytes=b"fake pdf content",
            ),
            "DOCUMENT_PARSER_TIMEOUT",
        ),
        (
            lambda: analyze_cv_with_agent_service(
                cv_text="Candidate has Python and FastAPI experience building backend services.",
                jd_text="We need a Python engineer with FastAPI experience building backend services.",
            ),
            "AGENT_SERVICE_TIMEOUT",
        ),
    ],
)
def test_internal_service_timeout_returns_504(monkeypatch, call, expected_code):
    class TimingOutAsyncClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, *args, **kwargs):
            request = httpx.Request("POST", "http://internal-service.test")
            raise httpx.ReadTimeout("timed out", request=request)

    monkeypatch.setattr(
        "app.modules.analyze.service.httpx.AsyncClient",
        TimingOutAsyncClient,
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(call())

    assert exc_info.value.status_code == 504
    assert exc_info.value.detail["code"] == expected_code
