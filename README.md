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
* [Changelog](CHANGELOG.md)

## Tech Stack

* Frontend: Next.js
* Backend: FastAPI microservices
* Agent Workflow: LangGraph
* AI API: Gemini
* Database: Supabase PostgreSQL
* Storage: Supabase Storage
* Deployment: Vercel + AWS

## Backend Services

The backend is organized as FastAPI microservices:

* `backend/api-gateway`: public entry point for frontend requests.
* `backend/document-parser-service`: internal service for extracting text from uploaded PDF documents.
* `backend/agent-service`: planned internal service for running the LangGraph CV/JD analysis workflow.

For detailed service responsibilities, see [Architecture Draft](docs/ARCHITECTURE_DRAFT.md).  
For endpoint contracts, see [API Draft](docs/API_DRAFT.md).

## Local Development

### API Gateway

```bash
cd backend/api-gateway
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local environment file:

```bash
cp .env.example .env
```

Run service:

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```txt
http://127.0.0.1:8000/docs
```

### Document Parser Service

```bash
cd backend/document-parser-service
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local environment file:

```bash
cp .env.example .env
```

Run service:

```bash
uvicorn app.main:app --reload --port 8001
```

Open:

```txt
http://127.0.0.1:8001/docs
```
