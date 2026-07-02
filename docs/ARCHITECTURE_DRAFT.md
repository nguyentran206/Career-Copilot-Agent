# Architecture Draft

## Overview

Career Copilot Agent is an AI-powered system that analyzes a candidate's CV against a Job Description and returns a personalized action plan.

The system does not only return a fit score. It also decides what the candidate should do next based on the match level:

* High fit: generate a cover letter.
* Medium fit: suggest CV improvements and generate a cover letter.
* Low fit: suggest CV improvements and generate a learning roadmap.

---

## Deployment

* Frontend: Next.js on Vercel
* Backend: FastAPI microservices on AWS
* API Gateway: Public entry point for frontend requests
* Document Parser Service: Extracts raw text from uploaded PDF documents
* Agent Service: Runs LangGraph workflow for CV/JD analysis
* Database: Supabase PostgreSQL
* Storage: Supabase Storage
* AI API: Gemini API
* Embedding Model: Used for skill similarity matching

---

## Backend Services

### API Gateway

Responsibilities:

* Receive requests from the frontend
* Expose public API endpoints
* Handle CORS configuration
* Provide gateway health check
* Route requests to internal services in future phases

Current service port:

```text
http://127.0.0.1:8000
```

Current endpoint:

```text
GET /api/v1/health
```

Future endpoints:

```text
POST /api/v1/analyze
GET /api/v1/session/{session_id}
```

---

### Document Parser Service

Responsibilities:

* Receive uploaded PDF documents
* Validate uploaded file type and size
* Extract raw text from PDF files
* Return extracted text and document metadata to API Gateway or Agent Service

Current service port:

```text
http://127.0.0.1:8001
```

Current endpoints:

```text
GET /api/v1/health
POST /api/v1/parse-document
```

Current MVP usage:

* Parse CV PDF into raw text.
* JD is currently expected as plain text in the main analysis flow.
* JD PDF parsing may be supported in a future phase.
* OCR is not included in the MVP.
* Scanned PDFs may return empty or very short text with a warning.

---

### Agent Service

Responsibilities:

* Parse CV text into structured information
* Parse JD text into structured requirements
* Match CV skills against JD requirements
* Calculate fit score from 0 to 100
* Evaluate fit level: `high`, `medium`, or `low`
* Generate CV improvement suggestions
* Generate cover letter for high and medium fit
* Generate learning roadmap for low fit
* Return final analysis result
* Save result to Supabase in a future phase

Planned service port:

```text
http://127.0.0.1:8002
```

---

## Main Flow

1. User uploads a CV PDF and enters Job Description text.
2. Frontend sends `cv_file` and `jd_text` to API Gateway.
3. API Gateway receives the request and validates the basic input.
4. API Gateway forwards the CV PDF to Document Parser Service.
5. Document Parser Service extracts raw text from the CV PDF.
6. Document Parser Service returns `cv_text`, metadata, and warnings.
7. API Gateway sends `cv_text` and `jd_text` to Agent Service.
8. LangGraph Agent parses the CV and JD into structured data.
9. Agent performs skill matching using embedding-based similarity.
10. Agent calculates a fit score from 0 to 100.
11. Agent identifies matched skills, missing skills, and weak areas.
12. Agent decides the response strategy based on fit score, skill gaps, and CV quality:

    * High fit: generate cover letter.
    * Medium fit: suggest CV improvements and generate cover letter.
    * Low fit: suggest CV improvements and generate learning roadmap.
13. Backend saves the analysis result to Supabase.
14. Frontend displays the personalized result.

---

## Agent Nodes

Planned LangGraph nodes:

* parse_cv_node
* parse_jd_node
* match_skills_node
* calculate_fit_score_node
* evaluate_fit_level_node
* suggest_improvements_node
* generate_cover_letter_node
* generate_roadmap_node
* save_result_node

---

## MVP Architecture Scope

Included in MVP:

* API Gateway foundation
* Document Parser Service foundation
* CV PDF text extraction
* JD text input
* LangGraph Agent pipeline
* Embedding-based skill matching
* Fit score calculation
* Conditional workflow based on fit level
* Basic frontend upload form
* Basic result display

Not included in MVP:

* Authentication
* Payment
* User dashboard
* Multi-user history
* Beautiful PDF report
* OCR for scanned PDFs
* JD PDF upload
* Advanced job queue system
* Advanced analytics
