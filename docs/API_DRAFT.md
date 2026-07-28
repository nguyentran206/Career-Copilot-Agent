# API Overview

All responses pass through the Gateway except internal health/service traffic. Gateway responses include `X-Request-ID`; analysis/session responses use `Cache-Control: no-store`.

| Exposure | Service | Method | Endpoint | Purpose |
|---|---|---|---|---|
| Public | Gateway | GET | `/api/v1/health` | Liveness |
| Public | Gateway | POST | `/api/v1/analyze` | Start temporary analysis; returns `202` + session ID |
| Public | Gateway | GET | `/api/v1/session/{session_id}` | Poll `processing`, `completed`, or `failed`, plus `expires_at` |
| Private | Parser | GET | `/api/v1/health` | Container health |
| Private | Parser | POST | `/api/v1/parse-document` | Extract a PDF |
| Private | Agent | GET | `/api/v1/health` | Container health |
| Private | Agent | POST | `/api/v1/analyze` | Analyze extracted CV text against JD |

`POST /api/v1/analyze` is multipart form data with required `cv_file` and exactly one of `jd_text` or `jd_file`. Both uploaded files must be text-based PDFs within their configured size limits. If `jd_file` is supplied, Gateway parses it before calling Agent. A completed payload includes `cv_parse_result` and optional `jd_parse_result`; extracted raw text is not returned publicly.

Important public errors include `SESSION_NOT_FOUND` (also covers expired sessions), `SESSION_CAPACITY_REACHED` (`503`), `ANALYZE_RATE_LIMITED` (`429`), and `ANALYSIS_CAPACITY_REACHED` (`429`). Capacity/rate responses include `Retry-After`.

The Agent response contract is `phase6-v2`. Its component fields are `skill_coverage_score`, `experience_relevance_score`, `project_relevance_score`, and `education_cert_relevance_score`. Detailed schemas remain in the Pydantic and TypeScript source models.
