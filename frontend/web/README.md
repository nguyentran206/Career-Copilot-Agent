# Career Copilot Web

Next.js TypeScript App Router frontend for the Career Copilot Agent MVP.

## Role

This app is the public UI layer. It lets a user upload a CV PDF, paste a Job Description, start an analysis session, poll the session status, and render the completed analysis result.

The frontend calls only API Gateway. It does not call Document Parser Service or Agent Service directly.

For backend endpoint ownership and detailed contracts, see:

* [API Draft](../../docs/API_DRAFT.md)
* [API Gateway README](../../backend/api-gateway/README.md)

## Environment

Create a local env file:

```text
cp .env.example .env.local
```

Default value:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Local Development

Install dependencies:

```text
npm install
```

Run the frontend:

```text
npm run dev
```

Open:

```text
http://localhost:3000
```

Backend services should be running separately:

```text
API Gateway:              http://127.0.0.1:8000
Document Parser Service:  http://127.0.0.1:8001
Agent Service:            http://127.0.0.1:8002
```

## Implemented Flow

```text
User uploads CV PDF + enters JD text
→ Frontend POSTs multipart/form-data to API Gateway /api/v1/analyze
→ API Gateway returns session_id with processing status
→ Frontend polls API Gateway /api/v1/session/{session_id}
→ Frontend renders completed result or a friendly error
```

## Notes

This is an MVP UI. It intentionally does not include auth, dashboard history, persistence, or direct service-to-service controls.
