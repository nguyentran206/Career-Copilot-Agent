# Career Copilot Agent

AI-powered career assistant that analyzes a candidate's CV against a Job Description and returns a personalized action plan based on job fit.

The system extracts text from a CV PDF, analyzes it against a Job Description, calculates a fit score, identifies matched and missing skills, and recommends the next best action for the candidate.

## Product Goal

Career Copilot Agent helps candidates understand how well their CV matches a Job Description and what they should do next to improve their chance.

For detailed MVP scope, input/output, and conditional outcomes, see [MVP Scope](docs/MVP_SCOPE.md).

## Documentation

* [MVP Scope](docs/MVP_SCOPE.md)
* [Architecture Draft](docs/ARCHITECTURE_DRAFT.md)
* [API Draft](docs/API_DRAFT.md)
* [Implementation Status](docs/IMPLEMENTATION_STATUS.md)
* [Roadmap](docs/roadmap/README.md)
* [Changelog](CHANGELOG.md)

## Tech Stack

Current backend foundation:

* FastAPI microservices
* PDF text extraction
* Deterministic rule-based analysis baseline

Planned AI and infrastructure components:

* LangGraph
* Gemini
* Embedding-based semantic matching
* Supabase
* Next.js
* AWS and Vercel

For detailed implementation progress, see [Implementation Status](docs/IMPLEMENTATION_STATUS.md).

## Backend Services

The backend is organized as FastAPI microservices:

* `backend/api-gateway`: public entry point for frontend requests.
* `backend/document-parser-service`: internal service for extracting text from uploaded PDF documents.
* `backend/agent-service`: internal service that currently exposes a deterministic rule-based CV/JD analysis baseline. LangGraph, Gemini, and embedding-based matching are planned for later phases.

Agent Service currently uses a deterministic rule-based baseline and is not yet connected to API Gateway.

For detailed implementation progress, see [Implementation Status](docs/IMPLEMENTATION_STATUS.md).

For detailed service responsibilities, see [Architecture Draft](docs/ARCHITECTURE_DRAFT.md).  

For the API overview, see [API Draft](docs/API_DRAFT.md).

For detailed request/response contracts, see each service README.

## Local Development

Run each backend service in a separate terminal:

```text
API Gateway:              http://127.0.0.1:8000
Document Parser Service:  http://127.0.0.1:8001
Agent Service:            http://127.0.0.1:8002
```

For installation, environment configuration, testing, and run commands, see:

* [API Gateway README](backend/api-gateway/README.md)
* [Document Parser Service README](backend/document-parser-service/README.md)
* [Agent Service README](backend/agent-service/README.md)
