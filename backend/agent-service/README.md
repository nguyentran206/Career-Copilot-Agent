# Agent Service

Private FastAPI/LangGraph service that analyzes extracted CV text against a JD. It has no database and does not retain request content.

## Workflow

CV and JD parsing run in parallel. Gemini structured parsing is optional; deterministic parsing is the fallback. Matching uses exact aliases/taxonomy plus optional batched Gemini embeddings. Only the selected cover-letter or roadmap branch is generated. Multilingual source input is normalized into canonical English matching fields when Gemini is available; otherwise the workflow lowers confidence and marks uncertain JD priorities as unknown.

The JD is the only source of scored job requirements. No occupational dataset or inferred occupation requirement is used.

## `phase6-v2` score

Each JD skill has a fixed classification weight:

- required: `1.00`
- preferred: `0.65`
- unknown: `0.45`

Skill coverage is the weighted mean of CV evidence scores. The raw fit score dynamically normalizes only enabled components:

```text
skill_coverage_score             65%
experience_relevance_score       20%
project_relevance_score          10%
education_cert_relevance_score    5%
```

Required-skill guardrails prevent a high/medium result when required evidence is insufficient; a missing critical required skill also caps the result. Thresholds are high `>=75`, medium `>=50`, low `<50`. `score_confidence` describes analysis confidence and is separate from fit. The score is decision support, not a hiring decision.

## Local development

```bash
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8002
pytest -q
```

Copy `.env.example` to `.env`. Gemini and embeddings can be disabled for a fully deterministic run. Production values are documented in `.env.production.example`.

## Docker

```bash
docker build -t career-copilot-agent-service .
docker run --rm -p 8002:8002 career-copilot-agent-service
```

In production this port must remain private. Requests and responses carry `X-Request-ID`; structured logs contain metadata/timing only, not raw CV/JD bodies.
