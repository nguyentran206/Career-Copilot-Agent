# Career Copilot API Gateway

API Gateway for the Career Copilot Agent microservice architecture.

## Responsibilities

* Receive requests from the frontend
* Expose public API endpoints
* Handle CORS configuration
* Provide gateway health check
* Route requests to internal services in future phases

## Current Endpoints

| Method | Endpoint         | Description                         |
| ------ | ---------------- | ----------------------------------- |
| GET    | `/api/v1/health` | Check if the API Gateway is running |

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| APP_NAME | Service name | Career Copilot API Gateway |
| APP_ENV | Environment | development |
| APP_VERSION | App version | 0.1.0 |
| API_PREFIX | API prefix | /api/v1 |
| HOST | Server host | 127.0.0.1 |
| PORT | Server port | 8000 |
| FRONTEND_URL | Frontend origin for CORS | http://localhost:3000 |
| DOCUMENT_PARSER_SERVICE_URL | Internal Document Parser URL | http://127.0.0.1:8001 |
| AGENT_SERVICE_URL | Internal Agent Service URL | http://127.0.0.1:8002 |
| REQUEST_TIMEOUT_SECONDS | Internal request timeout | 60 |

## Local Development

### 1. Navigate to API Gateway

```bash
cd backend/api-gateway
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 6. Run server

```bash
uvicorn app.main:app --reload --port 8000
```

### 7. Open API Gateway

Health check:

```txt
http://127.0.0.1:8000/api/v1/health
```

API documentation:

```txt
http://127.0.0.1:8000/docs
```

## Current Status

The API Gateway currently provides only the health check endpoint.
Routing to internal services will be added in future phases.
