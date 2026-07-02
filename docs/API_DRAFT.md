# API Draft

## Overview

This document defines the initial API contract for the Career Copilot Agent MVP.

The system follows a microservice-based backend architecture:

```text
Frontend → API Gateway → Document Parser Service → Agent Service → Gemini/Supabase
```

The API Gateway exposes public endpoints to the frontend. Internal services such as Document Parser Service and Agent Service are called by the API Gateway or backend workflow.

---

## Public API Gateway Endpoints

### POST /api/v1/analyze

Analyze a CV against a Job Description.

This endpoint receives the user's CV PDF and Job Description text, then starts the analysis workflow.

### Request

Content type: `multipart/form-data`

| Field   | Type     | Required | Description                |
| ------- | -------- | -------- | -------------------------- |
| cv_file | PDF file | Yes      | Candidate CV in PDF format |
| jd_text | string   | Yes      | Job Description text       |

### Response

```json
{
  "session_id": "string",
  "status": "processing"
}
```

---

### GET /api/v1/session/{session_id}

Get the analysis status and result by session ID.

### Path Parameters

| Parameter  | Type   | Required | Description         |
| ---------- | ------ | -------- | ------------------- |
| session_id | string | Yes      | Analysis session ID |

### Response: Processing

```json
{
  "session_id": "string",
  "status": "processing",
  "result": null
}
```

### Response: Completed

```json
{
  "session_id": "string",
  "status": "completed",
  "result": {
    "fit_score": 78,
    "fit_level": "medium",
    "parsed_cv": {},
    "parsed_jd": {},
    "matched_skills": ["Python", "FastAPI"],
    "missing_skills": ["AWS", "Docker"],
    "cv_improvement_suggestions": [],
    "cover_letter": "Generated cover letter content...",
    "learning_roadmap": null
  }
}
```

### Conditional Result Fields

`cover_letter` and `learning_roadmap` are conditional fields.

| Fit Level | cover_letter | learning_roadmap |
|---|---|---|
| high | string | null |
| medium | string | null |
| low | null | array |

Non-applicable fields should be returned as `null`.

### Response: Failed

```json
{
  "session_id": "string",
  "status": "failed",
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Unable to complete analysis."
  }
}
```

---

## Internal Service Endpoints

### Document Parser Service

#### POST /api/v1/parse-document

Extract raw text content from an uploaded PDF document.

This endpoint is owned by `document-parser-service`.

### Request

Content type: `multipart/form-data`

| Field         | Type     | Required | Description                                      |
| ------------- | -------- | -------- | ------------------------------------------------ |
| file          | PDF file | Yes      | PDF document to parse                            |
| document_type | string   | No       | Optional document type, for example `cv` or `jd` |

### Successful Response

```json
{
  "filename": "cv.pdf",
  "document_type": "cv",
  "content_type": "application/pdf",
  "file_size_bytes": 245321,
  "page_count": 2,
  "text": "Extracted CV text here...",
  "text_length": 5421,
  "warnings": []
}
```

### Response With Warning

If the PDF appears to be scanned or contains too little extractable text, the service returns a successful response with a warning.

```json
{
  "filename": "cv_scan.pdf",
  "document_type": "cv",
  "content_type": "application/pdf",
  "file_size_bytes": 512331,
  "page_count": 2,
  "text": "",
  "text_length": 0,
  "warnings": [
    "NO_TEXT_EXTRACTED_OR_SCANNED_PDF"
  ]
}
```

---

## MVP Notes

* Current MVP input is CV PDF and JD text.
* JD PDF upload is not included in the MVP.
* Document Parser Service is designed generically and may support JD PDF parsing in a future phase.
* OCR is not included in the MVP.
* Scanned PDFs may return empty or short text with a warning.
* API Gateway currently exposes public API endpoints.
* Document Parser Service and Agent Service are internal backend services.
* Session/job persistence design may be simplified during early MVP implementation.
* The initial MVP may use basic in-memory or database-backed session tracking before introducing a production-grade job queue.
