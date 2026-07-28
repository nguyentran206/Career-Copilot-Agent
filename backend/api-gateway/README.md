# API Gateway

The only public backend service. It validates uploads/JDs, creates anonymous temporary sessions, calls Parser then Agent in a background task, and exposes polling.

## Runtime contract

- `POST /api/v1/analyze`: multipart required `cv_file` plus exactly one of `jd_text` or `jd_file`; returns `202`, `session_id`, `processing`.
- `GET /api/v1/session/{id}`: returns status/result/error and `expires_at`.
- Both analysis responses are `no-store`; every request has `X-Request-ID`.
- Parser read timeout: 30 seconds. Agent read timeout: 150 seconds.

When `jd_file` is supplied, Gateway sends it to Document Parser with `document_type=jd`, validates the extracted text, and then calls Agent. `MAX_CV_FILE_SIZE_MB` and `MAX_JD_FILE_SIZE_MB` default to 5.

Sessions live only in this process. Default TTL is 30 minutes and capacity is 500. Expired entries are removed lazily; completing/failing a session resets its TTL. A restart deletes everything. Rate windows and concurrency counters are also in memory, so production must use exactly one Gateway worker and one replica.

Default protection is 10 accepted starts per client per 60 seconds and 3 active analyses globally. Rejections return `429` with `Retry-After`; a full session store returns `503` with `Retry-After`.

## Local development

```bash
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
pytest -q
```

Start Parser on 8001 and Agent on 8002 first. Copy `.env.example` to `.env`; see `.env.production.example` for production settings.

## Docker

The Docker command deliberately uses one worker:

```bash
docker build -t career-copilot-api-gateway .
docker run --rm -p 8000:8000 career-copilot-api-gateway
```

For the full private-network topology, use the repository `docker-compose.yml`. Set `FRONTEND_URL` to the exact Vercel origin.
