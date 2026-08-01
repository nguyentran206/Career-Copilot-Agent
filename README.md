# Career Copilot Agent

Career Copilot analyzes a CV PDF against either pasted Job Description text or a text-based JD PDF, explains the fit score, identifies matched and missing skills, and returns either a cover-letter draft or a learning roadmap.

## Current release candidate

The product flow is complete through Phase 6 and is prepared for deployment validation:

- Next.js frontend intended for Vercel.
- CV PDF upload with exactly one JD source: pasted text or a text-based PDF.
- Three long-running FastAPI Docker services: public API Gateway plus private Document Parser and Agent services.
- LangGraph JD-first analysis, optional Gemini structured parsing/generation and embeddings, with deterministic fallbacks.
- Versioned `phase6-v2` scoring. No external occupation taxonomy is used.
- Anonymous, in-memory sessions: 30-minute TTL, maximum 500 sessions, no user account or application database.
- One Gateway worker/replica is required because sessions, rate limits, and concurrency counters are process-local.
- Request IDs, structured timing logs, no-store responses, request rate limiting, and analysis concurrency protection.

No cloud resources are created by this repository. The intended topology is Vercel for `frontend/web` and a container platform that can run all three backend containers continuously on one private network.

## Run with Docker

```bash
docker compose up --build
```

The Gateway is published at `http://localhost:8000`; the two internal services are not published to the host. Set `FRONTEND_URL`, `GEMINI_ENABLED`, `GEMINI_API_KEY`, and embedding variables in the deployment environment as needed.

## Documentation

- [Implementation status](docs/IMPLEMENTATION_STATUS.md)
- [Architecture](docs/ARCHITECTURE_DRAFT.md)
- [API overview](docs/API_DRAFT.md)
- [Deployment checklist](docs/DEPLOYMENT_CHECKLIST.md)
- [Agent scoring](backend/agent-service/README.md)
- [API Gateway](backend/api-gateway/README.md)
- [Frontend](frontend/web/README.md)
