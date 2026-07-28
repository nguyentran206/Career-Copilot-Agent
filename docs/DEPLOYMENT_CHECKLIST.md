# Deployment Checklist

## Before creating cloud resources

- Run backend tests, frontend lint/typecheck/build/audit, and all three Docker builds in CI.
- Run `docker compose up --build` and smoke-test upload, polling, expiry, errors, and request IDs.
- Choose a container platform that supports three continuously running containers, private service discovery/networking, health checks, and at least a 150-second upstream response window.
- Configure exactly one Gateway worker and one Gateway replica.
- Confirm the public reverse proxy accepts at least the combined CV/JD upload limit plus multipart overhead (at least 12 MB with the current 5 MB per-file defaults). The long analysis itself happens after the `202` response.

## Backend platform

- Publish only Gateway port 8000. Keep Parser 8001 and Agent 8002 private.
- Set service URLs to private DNS names and retain parser/agent timeouts `30`/`150` seconds.
- Set `FRONTEND_URL` to the exact Vercel production origin for CORS.
- Store `GEMINI_API_KEY` in the platform secret manager, never in an image or committed env file.
- Enable TLS on the public Gateway domain and verify health checks/restart policy.
- Configure log collection and search by `request_id`; verify logs do not contain CV/JD bodies.

## Vercel

- Import `frontend/web` as the project root.
- Set `NEXT_PUBLIC_API_BASE_URL` to the HTTPS Gateway origin and redeploy after changes.
- Confirm the Gateway CORS origin matches the final Vercel production URL (and explicitly decide how preview URLs are handled).

## Release smoke test

- Test pasted JDs and one-page text-based JD PDFs, including Vietnamese/mixed-language input.
- Confirm start returns `202`, `Cache-Control: no-store`, and `X-Request-ID`.
- Confirm polling completes within the 240-second frontend window and the result says `phase6-v2`.
- Confirm friendly behavior for expired sessions, rate limit, capacity, parser timeout, and agent timeout.
- Restart Gateway and confirm the documented loss of temporary sessions is acceptable.

Rollback by redeploying the previous immutable backend images and previous Vercel deployment. Session results are ephemeral and cannot be recovered after a Gateway restart.
