from fastapi.testclient import TestClient

from unittest.mock import AsyncMock, patch

from app.modules.analyze.schemas import DocumentParserResponse

from fastapi.testclient import TestClient

from fastapi import HTTPException, status

from app.main import app


client = TestClient(app)

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
    files = {
        "cv_file": ("cv.pdf", b"fake pdf content", "application/pdf")
    }

    response = client.post(
        "/api/v1/analyze",
        files=files,
        data={"jd_text": "     "},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JD_TEXT_REQUIRED"


def test_analyze_with_too_short_jd_text():
    files = {
        "cv_file": ("cv.pdf", b"fake pdf content", "application/pdf")
    }

    response = client.post(
        "/api/v1/analyze",
        files=files,
        data={"jd_text": "Python"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "JD_TEXT_TOO_SHORT"

def test_analyze_success_with_mocked_document_parser():
    jd_text = "We are looking for a Python developer with FastAPI experience and backend API development skills."

    mock_parse_result = DocumentParserResponse(
        filename="cv.pdf",
        document_type="cv",
        content_type="application/pdf",
        file_size_bytes=12345,
        page_count=1,
        text="This is extracted CV text with Python and FastAPI experience.",
        text_length=61,
        warnings=[],
    )

    with patch(
        "app.modules.analyze.routes.parse_cv_with_document_parser",
        new=AsyncMock(return_value=mock_parse_result),
    ):
        files = {
            "cv_file": ("cv.pdf", b"fake pdf content", "application/pdf")
        }

        response = client.post(
            "/api/v1/analyze",
            files=files,
            data={
                "jd_text": jd_text
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
    assert data["message"] == "CV parsed successfully. Agent analysis is not implemented yet."
    assert data["cv_parse_result"]["filename"] == "cv.pdf"
    assert data["cv_parse_result"]["document_type"] == "cv"
    assert data["cv_parse_result"]["page_count"] == 1
    assert data["cv_parse_result"]["text_length"] == 61
    assert data["jd_text_length"] == len(jd_text)
    assert "Python" in data["text_preview"]


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
        files = {
            "cv_file": ("cv.pdf", b"fake pdf content", "application/pdf")
        }

        response = client.post(
            "/api/v1/analyze",
            files=files,
            data={
                "jd_text": "We are looking for a Python developer with backend API development experience."
            },
        )

    assert response.status_code == 503

    data = response.json()
    assert data["detail"]["code"] == "DOCUMENT_PARSER_UNAVAILABLE"

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