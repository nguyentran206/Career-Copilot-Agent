# Roadmap

Phases 1–6 are complete in source. Phase 6 now represents the deployment-ready anonymous MVP: JD-first `phase6-v2`, multilingual analysis, temporary sessions, public safeguards, Docker packaging, CI, and deployment documentation.

The next phase is release execution—not additional product functionality:

1. pass CI and local Compose smoke tests;
2. choose/configure a long-running container platform;
3. deploy three backend containers with only Gateway public and one Gateway worker/replica;
4. deploy `frontend/web` to Vercel;
5. configure CORS, secrets, TLS, logs, domains, and production smoke tests.

Accounts, database persistence, Redis/queue, OCR, payments, and durable history remain deliberately out of scope until product usage demonstrates a need.
