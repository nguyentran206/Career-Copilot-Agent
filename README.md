# Career Copilot Agent

AI-powered career assistant that analyzes a candidate's CV against a Job Description and returns a personalized action plan based on job fit.

The system extracts text from a CV PDF, analyzes it against a Job Description, calculates a fit score, identifies matched and missing skills, and recommends the next best action for the candidate.

## Product Goal

Career Copilot Agent helps candidates answer three questions:

1. How well does my CV match this job?
2. What skills or requirements am I missing?
3. What should I do next to improve my chance?

The system provides different outputs based on the candidate's fit level:

* High fit: generate a cover letter.
* Medium fit: suggest CV improvements and generate a cover letter.
* Low fit: suggest CV improvements and generate a learning roadmap.

## Documentation

* [MVP Scope](docs/MVP_SCOPE.md)
* [Architecture Draft](docs/ARCHITECTURE_DRAFT.md)
* [API Draft](docs/API_DRAFT.md)
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

### API Gateway

Public entry point for frontend requests.

Responsibilities:

* Receive requests from the frontend
* Expose public API endpoints
* Handle CORS configuration
* Provide gateway health check
* Route requests to internal services in future phases

Service path:

```txt
backend/api-gateway
```

Current endpoint:

```txt
GET /api/v1/health
```

Local URL:

```txt
http://127.0.0.1:8000
```

### Document Parser Service

Internal service responsible for extracting raw text from uploaded PDF documents.

Responsibilities:

* Receive uploaded PDF documents
* Validate uploaded file type and size
* Extract raw text from PDF files
* Return extracted text and document metadata

Service path:

```txt
backend/document-parser-service
```

Current endpoints:

```txt
GET /api/v1/health
POST /api/v1/parse-document
```

Local URL:

```txt
http://127.0.0.1:8001
```

### Agent Service

Planned internal service responsible for running the LangGraph CV/JD analysis workflow.

Responsibilities:

* Parse CV text into structured information
* Parse JD text into structured requirements
* Match skills using embedding-based similarity
* Calculate fit score
* Generate CV improvement suggestions
* Generate cover letter for high and medium fit
* Generate learning roadmap for low fit

Planned local URL:

```txt
http://127.0.0.1:8002
```

## Current Status

MVP is in development.

Completed foundation:

* Project planning documents
* MVP scope
* Architecture draft
* API draft
* API Gateway FastAPI structure
* API Gateway health check endpoint
* API Gateway environment configuration
* Document Parser Service FastAPI structure
* Document Parser health check endpoint
* Document Parser PDF text extraction endpoint
* Document Parser API contract documentation

Not implemented yet:

* Frontend Next.js application
* API Gateway routing to Document Parser Service
* Agent Service
* LangGraph workflow
* Gemini integration
* Embedding-based skill matching
* Fit score calculation
* Supabase integration
* Result persistence
* Basic session status tracking
* End-to-end `/analyze` flow

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

## MVP Flow

Planned end-to-end flow:

```txt
User uploads CV PDF and enters JD text
→ Frontend sends request to API Gateway
→ API Gateway sends CV PDF to Document Parser Service
→ Document Parser Service returns extracted CV text
→ Agent Service analyzes CV text against JD text
→ System returns fit score, matched skills, missing skills, suggestions, and conditional output
→ Frontend displays the result
```

## MVP Limitations

* Authentication is not included.
* Payment is not included.
* User dashboard is not included.
* Multi-user history is not included.
* OCR for scanned PDFs is not included.
* JD PDF upload is not included in the MVP.
* Beautiful PDF report generation is not included.
