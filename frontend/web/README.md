# Career Copilot Web

Next.js App Router frontend intended for Vercel. It calls only the public API Gateway, starts an analysis, and polls the temporary session for up to 240 seconds.

The UI accepts a CV PDF and lets the user choose either pasted JD text or a JD PDF. It explains the 30-minute in-memory privacy model, keeps session/language/scoring metadata out of the user-facing interface, maps expiry/rate/capacity errors to friendly text, and provides retry/clear controls. Results include a fit-score disclaimer.

## Local

```bash
npm ci
npm run dev
npm run lint
npm run typecheck
npm run build
npm audit --audit-level=high
```

Copy `.env.example` to `.env.local`. For Vercel, set `NEXT_PUBLIC_API_BASE_URL` to the public HTTPS Gateway origin; `.env.production.example` is the template.

No CV/JD is stored by Next.js or in browser storage. The browser sends the upload directly to Gateway and keeps only component state for the open page.
