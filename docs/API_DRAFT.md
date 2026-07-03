# API Draft

## Overview

This document defines the initial API contract for the Career Copilot Agent MVP.

The system follows a microservice-based backend architecture:

```text
Frontend → API Gateway
API Gateway → Document Parser Service
API Gateway → Agent Service
Agent Service → Gemini
Future: Agent Service/API Gateway → Supabase
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

Current implementation returns a temporary parser-based response. Full fit scoring and Agent analysis will be added in a later phase.

### Current Temporary Response

Current implementation returns a parser-based response. Full Agent analysis and session-based processing will be added in a later phase.

```json
{
  "status": "completed",
  "message": "CV parsed successfully. Agent analysis is not implemented yet.",
  "cv_parse_result": {
    "filename": "cv.pdf",
    "document_type": "cv",
    "content_type": "application/pdf",
    "file_size_bytes": 245321,
    "page_count": 2,
    "text_length": 5421,
    "warnings": []
  },
  "jd_text_length": 1200,
  "text_preview": "First 300 characters of extracted CV text..."
}
```

### Future Session-Based Response

```json
{
  "session_id": "string",
  "status": "processing"
}
```

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

`cv_improvement_suggestions`, `cover_letter`, and `learning_roadmap` depend on the fit level.

| Fit Level | cv_improvement_suggestions | cover_letter | learning_roadmap |
|---|---|---|---|
| high | [] | string | null |
| medium | array | string | null |
| low | array | null | array |

Rules:

* `cv_improvement_suggestions` should always be an array.
* If there are no CV improvement suggestions, return an empty array `[]`.
* Non-applicable object/string fields should be returned as `null`.

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


