from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_returns_expected_schema():
    payload = {
        "cv_text": (
            "I have experience with Python, SQL, Excel, dashboard building, "
            "data analysis, pandas, numpy, and business reporting projects."
        ),
        "jd_text": (
            "We are looking for a data analyst with Python, SQL, Excel, "
            "Power BI, dashboard, statistics, and data analysis skills."
        ),
    }

    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "fit_score" in data
    assert "fit_level" in data
    assert "score_breakdown" in data
    assert "parsed_cv" in data
    assert "parsed_jd" in data
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "cv_improvement_suggestions" in data
    assert "cover_letter" in data
    assert "learning_roadmap" in data


def test_analyze_rejects_short_cv_text():
    payload = {
        "cv_text": "short",
        "jd_text": (
            "We are looking for a data analyst with Python, SQL, Excel, "
            "Power BI, dashboard, statistics, and data analysis skills."
        ),
    }

    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 422


def test_analyze_rejects_short_jd_text():
    payload = {
        "cv_text": (
            "I have experience with Python, SQL, Excel, dashboard building, "
            "data analysis, pandas, numpy, and business reporting projects."
        ),
        "jd_text": "short",
    }

    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 422