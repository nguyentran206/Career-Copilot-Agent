# Career Copilot API Gateway

API Gateway for the Career Copilot Agent microservice architecture.

## Responsibilities

- Receive requests from the frontend
- Expose public API endpoints
- Handle CORS configuration
- Provide gateway health check
- Route requests to internal services in future phases

## Current Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Check if the API Gateway is running |

## Local Development

Create virtual environment:

```bash
python -m venv .venv
```

## Activate virtual environment

### Windows PowerShell
.venv\Scripts\Activate.ps1

### macOS/Linux
source .venv/bin/activate

## Install dependencies

pip install -r requirements.txt

## Run server

uvicorn app.main:app --reload --port 8000

## Open

http://127.0.0.1:8000/api/v1/health

http://127.0.0.1:8000/docs