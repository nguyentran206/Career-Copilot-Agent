# Architecture Draft

## Overview

Career Copilot Agent is an AI-powered system that analyzes a candidate's CV against a Job Description and returns a personalized action plan.

The system does not only return a fit score. The Agent Service follows the MVP decision rules defined in [MVP Scope](MVP_SCOPE.md) to choose the appropriate next-step recommendation.

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
POST /api/v1/analyze
```

Current POST /api/v1/analyze behavior:

```text
API Gateway receives CV PDF and JD text
→ calls Document Parser Service
→ returns temporary parser-based response
```

Future endpoints:

```text
GET /api/v1/session/{session_id}
```

---

### Document Parser Service

Responsibilities:

* Receive uploaded PDF documents
* Validate uploaded file type and size
* Extract raw text from PDF files
* Return extracted text and document metadata to API Gateway.

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
* Future: save analysis result to Supabase

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
12. Agent decides the response strategy based on fit score according to [MVP Scope](MVP_SCOPE.md).
13. Future phase: save the analysis result to Supabase.
14. Frontend displays the personalized result.

---

## Current Implemented Flow

```text
User uploads CV PDF and enters JD text through API Gateway Swagger
→ API Gateway calls Document Parser Service
→ Document Parser Service extracts CV text
→ API Gateway returns parser metadata, JD text length, and text preview
```

Full Agent analysis is not implemented yet.

---

## Agent Nodes

### MVP Nodes

* parse_cv_node
* parse_jd_node
* match_skills_node
* calculate_fit_score_node
* evaluate_fit_level_node
* suggest_improvements_node
* generate_cover_letter_node
* generate_roadmap_node

### Future Nodes

* save_result_node
