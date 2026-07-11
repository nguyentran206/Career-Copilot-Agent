from unittest.mock import AsyncMock, patch

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.main import app
from app.modules.analyze.schemas import AgentAnalyzeResponse, DocumentParserResponse


client = TestClient(app)


def build_parser_response(
    text: str = "This is extracted CV text with Python and FastAPI experience from backend API projects.",
    warnings: list[str] | None = None,
) -> DocumentParserResponse:
    return DocumentParserResponse(
        filename="cv.pdf",
        document_type="cv",
        content_type="application/pdf",
        file_size_bytes=12345,
        page_count=1,
        text=text,
        text_length=len(text),
        warnings=warnings or [],
    )


def build_agent_response() -> AgentAnalyzeResponse:
    return AgentAnalyzeResponse(
        fit_score=100,
        fit_level="high",
        score_breakdown={
            "required_skill_score": 100,
            "preferred_skill_score": 0,
            "experience_relevance_score": 0,
            "project_domain_relevance_score": 0,
            "education_cert_tool_score": 0,
        },
        parsed_cv={
            "skills": ["FastAPI", "Python"],
            "experience_summary": None,
            "projects": [],
            "education": [],
            "certifications": [],
        },
        parsed_jd={
            "required_skills": ["FastAPI", "Python"],
            "preferred_skills": [],
            "responsibilities": [],
            "domain_keywords": [],
        },
        skill_matches=[
            {
                "jd_skill": "Python",
                "resume_skill": "Python",
                "similarity": 1.0,
                "match_level": "strong",
                "importance": 1.0,
            },
            {
                "jd_skill": "FastAPI",
                "resume_skill": "FastAPI",
                "similarity": 1.0,
                "match_level": "strong",
                "importance": 1.0,
            },
        ],
        matched_skills=["FastAPI", "Python"],
        missing_skills=[],
        cv_improvement_suggestions=[],
        cover_letter="Cover letter generation will be implemented in a later phase.",
        learning_roadmap=None,
    )


def post_analyze(jd_text: str):
    files = {
        "cv_file": ("cv.pdf", b"fake pdf content", "application/pdf")
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


def test_analyze_success_with_mocked_parser_and_agent():
    jd_text = "We are looking for a Python developer with FastAPI experience and backend API development skills."

    mock_parse_result = build_parser_response()
    mock_agent_result = build_agent_response()

    with patch(
        "app.modules.analyze.routes.parse_cv_with_document_parser",
        new=AsyncMock(return_value=mock_parse_result),
    ), patch(
        "app.modules.analyze.routes.analyze_cv_with_agent_service",
        new=AsyncMock(return_value=mock_agent_result),
    ) as mock_agent_call:
        response = post_analyze(jd_text)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
    assert data["message"] == "CV parsed and analyzed successfully."
    assert data["cv_parse_result"]["filename"] == "cv.pdf"
    assert data["cv_parse_result"]["document_type"] == "cv"
    assert data["cv_parse_result"]["page_count"] == 1
    assert data["cv_parse_result"]["text_length"] == mock_parse_result.text_length
    assert data["analysis_result"]["fit_score"] == 100
    assert data["analysis_result"]["fit_level"] == "high"
    assert "text_preview" not in data

    mock_agent_call.assert_awaited_once_with(
        cv_text=mock_parse_result.text,
        jd_text=jd_text,
        parser_warnings=[],
    )


def test_analyze_sends_normalized_jd_text_to_agent():
    jd_text = "  We   are looking for a Python developer with     FastAPI experience and backend API development skills.  "
    normalized_jd_text = "We are looking for a Python developer with FastAPI experience and backend API development skills."

    mock_parse_result = build_parser_response()
    mock_agent_result = build_agent_response()

    with patch(
        "app.modules.analyze.routes.parse_cv_with_document_parser",
        new=AsyncMock(return_value=mock_parse_result),
    ), patch(
        "app.modules.analyze.routes.analyze_cv_with_agent_service",
        new=AsyncMock(return_value=mock_agent_result),
    ) as mock_agent_call:
        response = post_analyze(jd_text)

    assert response.status_code == 200
    mock_agent_call.assert_awaited_once_with(
        cv_text=mock_parse_result.text,
        jd_text=normalized_jd_text,
        parser_warnings=[],
    )


def test_analyze_when_document_parser_fails():
    parser_error = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "DOCUMENT_PARSER_UNAVAILABLE",
            "message": "Document Parser Service is unavailable.",
        },
    )

    with patch(
        "app.modules.analyze.routes.parse_cv_with_document_parser",
        new=AsyncMock(side_effect=parser_error),
    ):
        response = post_analyze(
            "We are looking for a Python developer with backend API development experience."
        )

    assert response.status_code == 503

    data = response.json()
    assert data["detail"]["code"] == "DOCUMENT_PARSER_UNAVAILABLE"


def test_analyze_when_extracted_cv_text_is_too_short():
    agent_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "code": "CV_TEXT_TOO_SHORT",
            "message": "Extracted CV text is too short for analysis. The PDF may be scanned or image-based.",
            "parser_warnings": ["NO_TEXT_EXTRACTED_OR_SCANNED_PDF"],
        },
    )

    with patch(
        "app.modules.analyze.routes.parse_cv_with_document_parser",
        new=AsyncMock(
            return_value=build_parser_response(
                text="too short",
                warnings=["NO_TEXT_EXTRACTED_OR_SCANNED_PDF"],
            )
        ),
    ), patch(
        "app.modules.analyze.routes.analyze_cv_with_agent_service",
        new=AsyncMock(side_effect=agent_error),
    ):
        response = post_analyze(
            "We are looking for a Python developer with backend API development experience."
        )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "CV_TEXT_TOO_SHORT"
    assert response.json()["detail"]["parser_warnings"] == ["NO_TEXT_EXTRACTED_OR_SCANNED_PDF"]


def test_analyze_when_agent_service_fails():
    agent_error = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "AGENT_SERVICE_UNAVAILABLE",
            "message": "Agent Service is unavailable.",
        },
    )

    with patch(
        "app.modules.analyze.routes.parse_cv_with_document_parser",
        new=AsyncMock(return_value=build_parser_response()),
    ), patch(
        "app.modules.analyze.routes.analyze_cv_with_agent_service",
        new=AsyncMock(side_effect=agent_error),
    ):
        response = post_analyze(
            "We are looking for a Python developer with backend API development experience."
        )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "AGENT_SERVICE_UNAVAILABLE"


def test_analyze_when_agent_service_returns_invalid_response():
    agent_error = HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "code": "AGENT_SERVICE_INVALID_RESPONSE",
            "message": "Agent Service returned an invalid response.",
        },
    )

    with patch(
        "app.modules.analyze.routes.parse_cv_with_document_parser",
        new=AsyncMock(return_value=build_parser_response()),
    ), patch(
        "app.modules.analyze.routes.analyze_cv_with_agent_service",
        new=AsyncMock(side_effect=agent_error),
    ):
        response = post_analyze(
            "We are looking for a Python developer with backend API development experience."
        )

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "AGENT_SERVICE_INVALID_RESPONSE"


def test_analyze_with_empty_cv_file():
    files = {
        "cv_file": ("cv.pdf", b"", "application/pdf")
    }

    response = client.post(
        "/api/v1/analyze",
        files=files,
        data={"jd_text": "We are looking for a Python developer with FastAPI experience."},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPTY_CV_FILE"
