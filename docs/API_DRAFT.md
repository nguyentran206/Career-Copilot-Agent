# API Draft

## Purpose

This document is the high-level API overview and endpoint registry for the Career Copilot Agent MVP.

It intentionally does not duplicate detailed request/response contracts. Detailed endpoint contracts, error responses, environment variables, and local run instructions are documented in each service README.

## Source of Truth Policy

| Information Type | Source of Truth |
|---|---|
| Current implementation progress | [Implementation Status](IMPLEMENTATION_STATUS.md) |
| System architecture and current/target flow | [Architecture Draft](ARCHITECTURE_DRAFT.md) |
| Endpoint registry and ownership | This document |
| Detailed endpoint contracts | Service README files |

## Current Runtime Topology

```text
Client
  → API Gateway
      → Document Parser Service
      → Agent Service
```

Current notes:

* API Gateway currently calls Document Parser Service to extract CV text.
* API Gateway then calls Agent Service to analyze extracted CV text against JD text.
* Agent Service also exposes its own deterministic analysis endpoint for direct local testing.

## Target MVP Topology

```text
Frontend
  → API Gateway
      → Document Parser Service
      → Agent Service
          → LangGraph workflow
          → Gemini
          → Embedding model

Future:
Agent Service/API Gateway
  → Supabase
```

---

## API Registry

| Service | Exposure | Method | Endpoint | Status | Detailed docs |
|---|---|---|---|---|---|
| API Gateway | Public | GET | `/api/v1/health` | Implemented | [API Gateway README](../backend/api-gateway/README.md) |
| API Gateway | Public | POST | `/api/v1/analyze` | Implemented synchronous parser + agent analysis response | [API Gateway README](../backend/api-gateway/README.md) |
| API Gateway | Public | GET | `/api/v1/session/{session_id}` | Planned | [API Gateway README](../backend/api-gateway/README.md) |
| Document Parser Service | Internal | GET | `/api/v1/health` | Implemented | [Document Parser Service README](../backend/document-parser-service/README.md) |
| Document Parser Service | Internal | POST | `/api/v1/parse-document` | Implemented | [Document Parser Service README](../backend/document-parser-service/README.md) |
| Agent Service | Internal/direct local | GET | `/api/v1/health` | Implemented | [Agent Service README](../backend/agent-service/README.md) |
| Agent Service | Internal/direct local | POST | `/api/v1/analyze` | Implemented deterministic baseline | [Agent Service README](../backend/agent-service/README.md) |

## Status Notes

* `POST /api/v1/analyze` in API Gateway currently returns a synchronous analysis response with status `completed`.
* Agent Service currently uses a deterministic rule-based analysis baseline and can still be tested directly.
* Session-based processing is planned for a later phase.
