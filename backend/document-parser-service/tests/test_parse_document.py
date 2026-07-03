from fastapi.testclient import TestClient

from pathlib import Path

from app.main import app


client = TestClient(app)


def test_parse_document_without_file():
    response = client.post("/api/v1/parse-document")

    assert response.status_code == 422


def test_parse_document_with_unsupported_file_type():
    files = {
        "file": ("sample.txt", b"hello world", "text/plain")
    }

    response = client.post(
        "/api/v1/parse-document",
        files=files,
        data={"document_type": "cv"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_parse_document_with_empty_pdf_file():
    files = {
        "file": ("empty.pdf", b"", "application/pdf")
    }

    response = client.post(
        "/api/v1/parse-document",
        files=files,
        data={"document_type": "cv"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPTY_FILE"


def test_parse_document_with_valid_pdf():
    pdf_path = Path(__file__).parent / "fixtures" / "sample_cv1.pdf"

    with pdf_path.open("rb") as pdf_file:
        files = {
            "file": ("sample_cv1.pdf", pdf_file, "application/pdf")
        }

        response = client.post(
            "/api/v1/parse-document",
            files=files,
            data={"document_type": "cv"},
        )

    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "sample_cv1.pdf"
    assert data["document_type"] == "cv"
    assert data["content_type"] == "application/pdf"
    assert data["file_size_bytes"] > 0
    assert data["page_count"] >= 1
    assert "text" in data
    assert "text_length" in data
    assert "warnings" in data