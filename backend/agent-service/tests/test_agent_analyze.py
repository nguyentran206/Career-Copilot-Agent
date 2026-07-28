from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def post_analyze(cv_text: str, jd_text: str):
    return client.post(
        "/api/v1/analyze",
        json={
            "cv_text": cv_text,
            "jd_text": jd_text,
        },
    )


def test_analyze_returns_expected_schema():
    response = post_analyze(
        cv_text=(
            "I have experience with Python, SQL, Excel, dashboard building, "
            "data analysis, pandas, numpy, and business reporting projects."
        ),
        jd_text=(
            "We are looking for a data analyst with Python, SQL, Excel, "
            "Power BI, dashboard, statistics, and data analysis skills."
        ),
    )

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


def test_analyze_high_fit_returns_cover_letter_without_roadmap():
    response = post_analyze(
        cv_text=(
            "Backend engineer with Python, FastAPI, PostgreSQL, REST API, "
            "Docker, and AWS experience building production services."
        ),
        jd_text=(
            "We need a backend engineer with Python, FastAPI, PostgreSQL, "
            "REST API, Docker, and AWS experience for production APIs."
        ),
    )

    assert response.status_code == 200

    data = response.json()
    assert 75 <= data["fit_score"] <= 100
    assert data["raw_fit_score"] == data["fit_score"]
    assert data["scoring_version"] == "phase6-v2"
    assert data["fit_level"] == "high"
    assert data["missing_skills"] == []
    assert data["cv_improvement_suggestions"] == []
    assert data["cover_letter"] is not None
    assert data["learning_roadmap"] is None


def test_analyze_medium_fit_returns_suggestions_and_cover_letter():
    response = post_analyze(
        cv_text=(
            "Backend developer with Python, SQL, and FastAPI experience "
            "building internal API services and database-backed applications."
        ),
        jd_text=(
            "We are hiring for Python, PostgreSQL, REST API, and Docker "
            "experience for a backend platform engineering role."
        ),
    )

    assert response.status_code == 200

    data = response.json()
    assert 50 <= data["fit_score"] < 75
    assert data["fit_level"] == "medium"
    assert data["missing_skills"] == ["Docker"]
    assert data["cv_improvement_suggestions"]
    assert data["cover_letter"] is not None
    assert data["learning_roadmap"] is None


def test_analyze_low_fit_returns_learning_roadmap_without_cover_letter():
    response = post_analyze(
        cv_text=(
            "Candidate has Excel reporting and stakeholder communication "
            "experience from operations and administrative projects."
        ),
        jd_text=(
            "This role requires AWS, Docker, LangGraph, RAG, Power BI, "
            "and Statistics experience for AI platform analytics work."
        ),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["fit_level"] == "low"
    assert data["cover_letter"] is None
    assert data["learning_roadmap"]
    assert len(data["missing_skills"]) >= 4


def test_analyze_partial_related_skill_matches_are_medium_fit():
    response = post_analyze(
        cv_text=(
            "Backend developer with SQL and FastAPI experience creating "
            "database-backed services and API endpoints for internal tools."
        ),
        jd_text=(
            "The job requires PostgreSQL and REST API experience for backend "
            "service development and production API design."
        ),
    )

    assert response.status_code == 200

    data = response.json()
    assert 50 <= data["fit_score"] < 75
    assert data["fit_level"] == "medium"
    assert data["missing_skills"] == []
    assert data["cv_improvement_suggestions"]
    assert {match["match_level"] for match in data["skill_matches"]} == {"partial"}


def test_analyze_no_known_jd_skills_returns_low_fit_with_generic_roadmap():
    response = post_analyze(
        cv_text=(
            "Candidate has Python and SQL experience from several reporting "
            "and automation projects across business operations."
        ),
        jd_text=(
            "We need a thoughtful teammate with curiosity, ownership, clear "
            "communication, collaboration, and problem solving habits."
        ),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["fit_score"] == 0
    assert data["fit_level"] == "low"
    assert data["parsed_jd"]["required_skills"] == []
    assert data["skill_matches"] == []
    assert data["cover_letter"] is None
    assert data["learning_roadmap"]


def test_analyze_rejects_short_cv_text():
    response = post_analyze(
        cv_text="short",
        jd_text=(
            "We are looking for a data analyst with Python, SQL, Excel, "
            "Power BI, dashboard, statistics, and data analysis skills."
        ),
    )

    assert response.status_code == 422


def test_analyze_rejects_short_jd_text():
    response = post_analyze(
        cv_text=(
            "I have experience with Python, SQL, Excel, dashboard building, "
            "data analysis, pandas, numpy, and business reporting projects."
        ),
        jd_text="short",
    )

    assert response.status_code == 422
