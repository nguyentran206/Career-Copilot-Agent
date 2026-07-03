# Career Copilot Agent - MVP Scope

## Goal

Build an AI agent that analyzes a CV against a Job Description and returns a personalized action plan based on job fit.

The MVP should help candidates answer three questions:

1. How well does my CV match this job?
2. What skills or requirements am I missing?
3. What should I do next to improve my chance?

---

## Product Idea

The system receives a candidate's CV PDF and Job Description text. It extracts CV text, parses the CV and JD into structured information, matches skills using AI/embedding, calculates a fit score, and returns recommendations based on the candidate's fit level.

The system should support conditional outcomes:

* High fit: generate a cover letter.
* Medium fit: suggest CV improvements and generate a cover letter.
* Low fit: suggest CV improvements and generate a learning roadmap.

---

## Input

* CV file in PDF format
* Job Description text

---

## Output

* Extracted CV text
* Parsed CV information
* Parsed JD requirements
* Fit score from 0 to 100
* Fit level: `high`, `medium`, or `low`
* Matched skills
* Missing skills
* CV improvement suggestions
* Conditional output based on fit level:

  * High fit: cover letter
  * Medium fit: CV improvement suggestions and cover letter
  * Low fit: CV improvement suggestions and learning roadmap

---

## MVP Decision Rules

The system returns different recommendations based on the candidate's fit level:

| Fit Level | MVP Output |
|---|---|
| high | Fit score, matched/missing skills, and cover letter |
| medium | Fit score, matched/missing skills, CV improvement suggestions, and cover letter |
| low | Fit score, matched/missing skills, CV improvement suggestions, and learning roadmap |

---

## In Scope (MVP Features)

* **Frontend:** Basic frontend upload form and basic result display.
* **API Gateway:** Foundation exposing public API endpoints.
* **Document Parser Service:** Internal service foundation for PDF text extraction.
* **Agent Service:** Internal backend service running the LangGraph agent pipeline.
* **Core Logic:**
  * CV PDF text extraction
  * JD text input
  * CV & JD parsing
  * Embedding-based skill matching
  * Fit score calculation
  * Conditional workflow based on fit level
  * CV improvement suggestions
  * Cover letter generation (for high and medium fit)
  * Learning roadmap generation (for low fit)
* **Session Tracking:** Basic in-memory session status tracking for MVP.

---

## Out of Scope (Not in MVP)

* **User Management & Monetization:**
  * Authentication
  * Payment
  * User dashboard
  * Multi-user history
* **Advanced Document Handling:**
  * JD PDF upload (MVP only supports JD text)
  * OCR for scanned PDFs
  * Beautiful PDF report generation
* **System & Infrastructure:**
  * Advanced analytics
  * Advanced job queue system (Session/job persistence design is simplified for MVP)
  * Advanced session management
  * Production-grade deployment
  * CI/CD pipeline

---

## Technical & Implementation Notes

* Document Parser Service is designed generically and may support JD PDF parsing in a future phase.
* Since OCR is not included, scanned PDFs may return empty or short text along with a `NO_TEXT_EXTRACTED_OR_SCANNED_PDF` warning.
* API Gateway acts as the public entry point, while Document Parser and Agent Service operate strictly as internal backend services.
* The initial MVP uses in-memory session status tracking.
* Long-term result persistence with Supabase is not part of the initial MVP and will be added in a future phase.

---

## User Flow & Success Criteria

The MVP is considered successful when the following vertical slice (End-to-End Flow) works without requiring authentication, payment, or advanced history:

```text
User uploads CV PDF and enters JD text
→ Frontend sends request to API Gateway
→ API Gateway sends CV PDF to Document Parser Service
→ Document Parser Service returns extracted CV text
→ Agent Service analyzes CV text against JD text
→ System returns fit score, matched skills, missing skills, suggestions, and conditional output
→ Frontend displays the result
```

## Implementation Status

MVP is currently in development.

For current implementation progress, see [Implementation Status](IMPLEMENTATION_STATUS.md).
