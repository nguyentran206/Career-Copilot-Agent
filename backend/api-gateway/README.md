# Career Copilot API Gateway

API Gateway for the Career Copilot Agent microservice architecture.

This README explains how to run and configure API Gateway locally.

## Responsibilities

* Receive requests from the frontend
* Expose public API endpoints
* Handle CORS configuration
* Provide gateway health check
* Route requests to internal services

## Current Endpoints

| Method | Endpoint         | Description                         |
| ------ | ---------------- | ----------------------------------- |
| GET    | `/api/v1/health` | Check if the API Gateway is running |
| POST | `/api/v1/analyze` | Start a CV/JD analysis session |
| GET | `/api/v1/session/{session_id}` | Get analysis session status and result |

## API Contract

This README is the canonical detailed API contract for API Gateway.

For the system-wide endpoint registry, see [API Draft](../../docs/API_DRAFT.md).

### Health Check

```http
GET /api/v1/health
```

Successful response:

```json
{
  "status": "ok",
  "service": "Career Copilot API Gateway",
  "version": "0.1.0",
  "environment": "development"
}
```

### Analyze CV Against Job Description

```http
POST /api/v1/analyze
```

Current behavior:

```text
API Gateway receives CV PDF and JD text
→ validates the basic request
→ creates an in-memory analysis session
→ returns session_id with status processing
→ runs Document Parser Service and Agent Service in a background task
```

This is currently a session-based MVP flow backed by an in-memory session store.

Request content type:

```text
multipart/form-data
```

Request fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `cv_file` | PDF file | Yes | Candidate CV in PDF format |
| `jd_text` | string | Yes | Job Description text |

Successful response:

Status code:

```text
202 Accepted
```

```json
{
  "session_id": "string",
  "status": "processing"
}
```

Immediate validation error responses:

| Status Code | Error Code | Description |
|---|---|---|
| 400 | `JD_TEXT_REQUIRED` | Job Description text is blank after normalization. |
| 400 | `JD_TEXT_TOO_SHORT` | Job Description text is shorter than the minimum allowed length. |
| 400 | `EMPTY_CV_FILE` | Uploaded CV file is empty. |
| 413 | `JD_TEXT_TOO_LONG` | Job Description text exceeds the maximum allowed length. |
| 413 | `CV_FILE_TOO_LARGE` | Uploaded CV file exceeds the API Gateway size limit. |
| 422 | FastAPI validation error | Required multipart field `cv_file` or `jd_text` is missing. |

Parser and Agent errors are stored in the session as `failed` results because they happen inside the background analysis task.

### Get Analysis Session

```http
GET /api/v1/session/{session_id}
```

Processing response:

```json
{
  "session_id": "string",
  "status": "processing",
  "result": null,
  "error": null
}
```

Completed response:

```json
{
  "session_id": "string",
  "status": "completed",
  "result": {
    "cv_parse_result": {
      "filename": "cv.pdf",
      "document_type": "cv",
      "content_type": "application/pdf",
      "file_size_bytes": 245321,
      "page_count": 2,
      "text_length": 5421,
      "warnings": []
    },
    "analysis_result": {
      "fit_score": 78,
      "fit_level": "medium",
      "score_breakdown": {
        "required_skill_score": 78,
        "preferred_skill_score": 0,
        "experience_relevance_score": 0,
        "project_domain_relevance_score": 0,
        "education_cert_tool_score": 0
      },
      "parsed_cv": {},
      "parsed_jd": {},
      "skill_matches": [],
      "matched_skills": ["Python", "FastAPI"],
      "missing_skills": ["Docker"],
      "cv_improvement_suggestions": [],
      "cover_letter": "Cover letter generation will be implemented in a later phase.",
      "learning_roadmap": null
    }
  },
  "error": null
}
```

Failed response:

```json
{
  "session_id": "string",
  "status": "failed",
  "result": null,
  "error": {
    "code": "AGENT_SERVICE_UNAVAILABLE",
    "message": "Agent Service is unavailable.",
    "detail": null
  }
}
```

Session error responses:

| Status Code | Error Code | Description |
|---|---|---|
| 404 | `SESSION_NOT_FOUND` | Analysis session does not exist in the in-memory store. |

Background failure codes may include:

| Error Code | Description |
|---|---|
| `DOCUMENT_PARSER_UNAVAILABLE` | API Gateway cannot reach Document Parser Service. |
| `DOCUMENT_PARSER_ERROR` | Document Parser Service returned an error while parsing the CV. |
| `DOCUMENT_PARSER_INVALID_RESPONSE` | Document Parser Service returned an invalid success response. |
| `CV_TEXT_TOO_SHORT` | Extracted CV text is too short for analysis, usually because the PDF is scanned or image-based. |
| `AGENT_SERVICE_UNAVAILABLE` | API Gateway cannot reach Agent Service. |
| `AGENT_SERVICE_ERROR` | Agent Service returned an error while analyzing the CV and JD. |
| `AGENT_SERVICE_INVALID_RESPONSE` | Agent Service returned an invalid success response. |

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| APP_NAME | Service name | Career Copilot API Gateway |
| APP_ENV | Environment | development |
| APP_VERSION | App version | 0.1.0 |
| API_PREFIX | API prefix | /api/v1 |
| HOST | Server host | 127.0.0.1 |
| PORT | Server port | 8000 |
| FRONTEND_URL | Frontend origin for CORS | http://localhost:3000 |
| DOCUMENT_PARSER_SERVICE_URL | Internal Document Parser URL | http://127.0.0.1:8001 |
| AGENT_SERVICE_URL | Internal Agent Service URL | http://127.0.0.1:8002 |
| REQUEST_TIMEOUT_SECONDS | Internal request timeout | 60 |
| MAX_CV_FILE_SIZE_MB | Maximum CV upload size in MB checked by API Gateway before calling Document Parser Service | 5 |

## Local Development

### 1. Navigate to API Gateway

```bash
cd backend/api-gateway
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
uvicorn app.main:app --reload --port 8000
```

### 7. Open API Gateway

Health check:

```txt
http://127.0.0.1:8000/api/v1/health
```

API documentation:

```txt
http://127.0.0.1:8000/docs
```

## Current Status

The API Gateway currently provides:

* Health check endpoint
* Analyze endpoint that starts an in-memory analysis session
* Session polling endpoint

Session persistence is not implemented yet. Sessions are stored in memory and are lost when API Gateway restarts.

## Related Documentation

* [Architecture Draft](../../docs/ARCHITECTURE_DRAFT.md)
* [API Draft](../../docs/API_DRAFT.md)
* [Implementation Status](../../docs/IMPLEMENTATION_STATUS.md)
