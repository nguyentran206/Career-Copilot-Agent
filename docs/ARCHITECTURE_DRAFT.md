# Architecture Draft

## Overview

Career Copilot Agent is an AI-powered system that analyzes a candidate's CV against a Job Description and returns a personalized action plan.

The system does not only return a fit score. The Agent Service follows the MVP decision rules defined in [MVP Scope](MVP_SCOPE.md) to choose the appropriate next-step recommendation.

---

## Architecture Status

This document describes both the current system topology and the target MVP architecture.

For detailed implementation progress, see [Implementation Status](IMPLEMENTATION_STATUS.md).

---

## Current Local Architecture

```text
Frontend
  → API Gateway
      → In-memory session store
      → Background analysis task
          → Document Parser Service
          → Agent Service
```

Current local frontend:

* Next.js TypeScript App Router app in `frontend/web`
* Default local URL: `http://localhost:3000`
* Calls only API Gateway at `NEXT_PUBLIC_API_BASE_URL`

Agent Service can also be tested directly during local development.

---

## Target MVP Architecture
```text
Frontend
  → API Gateway
      → Document Parser Service
      → Agent Service
          → LangGraph workflow
          → Gemini API
          → Embedding model

Future:
Agent Service/API Gateway
  → Supabase
```

Planned deployment:

* Frontend: Next.js on Vercel
* Backend: FastAPI microservices on AWS
* Database: Supabase PostgreSQL
* Storage: Supabase Storage

---

## Backend Services

### API Gateway

The API Gateway is the public backend entry point. It validates public requests, coordinates calls to internal services, and converts internal responses into the public API response.

The current implementation starts an in-memory analysis session, then runs Document Parser Service and Agent Service in a background analysis task.

For implementation and local development, see [API Gateway README](../backend/api-gateway/README.md).

---

### Document Parser Service

The Document Parser Service validates uploaded PDF documents and extracts raw text and document metadata.

It is responsible only for document parsing and does not perform CV/JD analysis.

For implementation and local development, see [Document Parser Service README](../backend/document-parser-service/README.md).

---

### Agent Service

The Agent Service analyzes extracted CV text against Job Description text, calculates job fit, and selects the appropriate recommendation output.

The current implementation uses a deterministic rule-based baseline. The target architecture introduces LangGraph orchestration, Gemini, and embedding-based semantic matching.

For implementation and local development, see [Agent Service README](../backend/agent-service/README.md).

---

## Current Implemented Flow

```text
User uploads CV PDF and enters JD text in the frontend
→ Frontend sends CV PDF and JD text to API Gateway
→ API Gateway validates the request
→ API Gateway creates an in-memory analysis session
→ API Gateway returns session_id with status processing
→ Background task sends the CV PDF to Document Parser Service
→ Document Parser Service extracts CV text and metadata
→ Background task sends extracted CV text and normalized JD text to Agent Service
→ Agent Service returns deterministic analysis result
→ API Gateway stores completed result or failed error in the session store
→ Frontend polls GET /api/v1/session/{session_id}
→ Frontend renders result or friendly error
```

Session tracking is implemented with an in-memory store for MVP. Sessions are lost when API Gateway restarts.

---

## Target MVP Flow

1. User uploads a CV PDF and enters Job Description text.
2. Frontend sends `cv_file` and `jd_text` to API Gateway.
3. API Gateway receives the request and validates the basic input.
4. API Gateway forwards the CV PDF to Document Parser Service.
5. Document Parser Service extracts raw text from the CV PDF.
6. Document Parser Service returns `cv_text`, metadata, and warnings.
7. API Gateway sends `cv_text` and `jd_text` to Agent Service.
8. Agent Service parses the CV and JD into structured data.
9. Agent performs skill matching.
10. Agent calculates a fit score from 0 to 100.
11. Agent identifies matched skills, missing skills, and weak areas.
12. Agent decides the response strategy based on fit score according to [MVP Scope](MVP_SCOPE.md).
13. Future phase: add LangGraph, Gemini, embedding-based matching, and Supabase persistence.
14. Frontend displays the personalized result.

---
