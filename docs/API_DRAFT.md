# API Draft

## POST /api/analyze

Analyze a CV against a Job Description.

### Request
- cv_file: PDF file
- jd_text: string

### Response
```json
{
  "session_id": "string",
  "status": "processing"
}
```

## GET /api/session/{session_id}

Get analysis status and result.

### Request
- cv_file: PDF file
- jd_text: string

### Response
```json
{
  "status": "completed",
  "result": {
    "fit_score": 78,
    "matched_skills": ["Python", "FastAPI"],
    "missing_skills": ["AWS", "Docker"],
    "suggestions": [],
    "roadmap": []
  }
}
```