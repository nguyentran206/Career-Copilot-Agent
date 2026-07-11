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
Client
  → API Gateway
      → Document Parser Service

Direct API client
  → Agent Service
```
Agent Service currently runs independently and is not yet connected to API Gateway.

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

The current implementation calls Document Parser Service. Agent Service integration is part of the target MVP flow.

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
Client sends CV PDF and JD text to API Gateway
→ API Gateway validates the request
→ API Gateway sends the CV PDF to Document Parser Service
→ Document Parser Service extracts CV text and metadata
→ API Gateway returns a parser-based temporary response
```

Agent Service can currently be tested directly through its own API, but it is not part of the API Gateway flow yet.

---

## Target MVP Flow

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
