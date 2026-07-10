# Agent Service

Internal FastAPI service responsible for analyzing extracted CV text against Job Description text.

## Responsibilities

- Receive `cv_text` and `jd_text` from API Gateway in the target MVP flow
- Support direct local testing through its own `/api/v1/analyze` endpoint in the current implementation
- Parse CV text into structured information
- Parse JD text into structured requirements
- Match CV skills against JD requirements
- Calculate fit score and fit level
- Return matched skills, missing skills, suggestions, and conditional output

## Current Status

This service currently provides foundation endpoints and deterministic rule-based scoring.

The Phase 2 deterministic baseline focuses on known skill extraction, related-skill matching, required-skill scoring, fit-level evaluation, and conditional output placeholders.
LangGraph, Gemini integration, embedding-based matching, and O*NET-based weighting are planned for later phases.

## Current Endpoints

| Method | Endpoint                 | Description                             |
| ------ | ------------------------ | --------------------------------------- |
| GET    | `/api/v1/health`         | Check service health                    |
| POST   | `/api/v1/analyze`        | Analyze CV text against JD text using the current deterministic baseline |

## API Contract

This README is the canonical detailed API contract for Agent Service.

For the system-wide endpoint registry, see [API Draft](../../docs/API_DRAFT.md).

### Health Check

```http
GET /api/v1/health
```

Successful response:

```json
{
  "status": "ok",
  "service": "agent-service",
  "version": "0.1.0"
}
```

### Analyze CV Against Job Description

```http
POST /api/v1/analyze
```

Current behavior:

```text
Agent Service receives extracted CV text and JD text
→ parses known skills using deterministic rules
→ matches required JD skills against CV skills
→ calculates a rule-based fit score and fit level
→ returns matched skills, missing skills, suggestions, and conditional output placeholders
```

LangGraph orchestration, Gemini integration, embedding-based semantic matching, and O*NET-based weighting are not implemented yet.

### Deterministic Baseline Rules

Skill extraction currently uses a curated rule-based catalog with aliases for common backend, data, and AI skills.

Matching rules:

| Match Level | Similarity | Description |
|---|---:|---|
| `strong` | `1.0` | Exact canonical skill match after alias normalization. |
| `partial` | `0.7` | Related deterministic match, for example `PostgreSQL` ↔ `SQL` or `REST API` ↔ `FastAPI`. |
| `missing` | `0.0` | Required JD skill was not found in the CV skill set. |

Current fit score baseline:

```text
fit_score = required_skill_score
```

`preferred_skill_score`, `experience_relevance_score`, `project_domain_relevance_score`, and `education_cert_tool_score` are kept in the response as placeholder fields with value `0.0`. They will be implemented in later phases.

Fit level thresholds:

| Fit Level | Rule |
|---|---|
| `high` | `fit_score >= 75` |
| `medium` | `50 <= fit_score < 75` |
| `low` | `fit_score < 50` |

Additional downgrade rules:

* If two or more required skills are missing, `high` is downgraded to `medium`.
* If four or more required skills are missing, the result is `low`.

Request content type:

```text
application/json
```

Request body:

```json
{
  "cv_text": "Extracted CV text with at least 50 non-whitespace characters.",
  "jd_text": "Job Description text with at least 50 non-whitespace characters."
}
```

Validation rules:

| Field | Rule |
|---|---|
| `cv_text` | Required, normalized whitespace, at least 50 non-whitespace characters |
| `jd_text` | Required, normalized whitespace, at least 50 non-whitespace characters |

Successful response:

```json
{
  "fit_score": 0,
  "fit_level": "low",
  "score_breakdown": {
    "required_skill_score": 0,
    "preferred_skill_score": 0,
    "experience_relevance_score": 0,
    "project_domain_relevance_score": 0,
    "education_cert_tool_score": 0
  },
  "parsed_cv": {
    "skills": [],
    "experience_summary": null,
    "projects": [],
    "education": [],
    "certifications": []
  },
  "parsed_jd": {
    "required_skills": [],
    "preferred_skills": [],
    "responsibilities": [],
    "domain_keywords": []
  },
  "skill_matches": [],
  "matched_skills": [],
  "missing_skills": [],
  "cv_improvement_suggestions": [],
  "cover_letter": null,
  "learning_roadmap": []
}
```

Conditional output rules:

| Fit Level | `cv_improvement_suggestions` | `cover_letter` | `learning_roadmap` |
|---|---|---|---|
| `high` | array | string placeholder | null |
| `medium` | array | string placeholder | null |
| `low` | array | null | array |

Error responses:

| Status Code | Description |
|---|---|
| 422 | Request body is missing required fields or text fields are shorter than the minimum length. |

## Local Development

### 1. Navigate to Agent Service

```bash
cd backend/agent-service
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 6. Run server

```bash
uvicorn app.main:app --reload --port 8002
```

### 7. Open Agent Service

Health check:

```txt
http://127.0.0.1:8002/api/v1/health
```

API Agent:

```txt
http://127.0.0.1:8002/docs
```
