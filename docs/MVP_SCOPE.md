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

## In MVP

* API Gateway foundation
* Document Parser Service foundation
* PDF text extraction for CV
* JD text input
* CV parsing
* JD parsing
* LangGraph agent pipeline
* Embedding-based skill matching
* Fit score calculation
* Conditional workflow based on fit level
* CV improvement suggestions
* Cover letter generation for high and medium fit
* Learning roadmap generation for low fit
* Basic FastAPI endpoint
* Basic frontend upload form
* Basic result display

---

## Not in MVP

* Authentication
* User dashboard
* Payment
* Advanced analytics
* Beautiful PDF report
* Multi-user history
* JD PDF upload
* OCR for scanned PDFs
* Advanced job queue system
* Advanced session management
* Production-grade deployment
* CI/CD pipeline

---

## Current Implementation Status

### Completed Foundation

* API Gateway initial FastAPI structure
* API Gateway health check endpoint
* API Gateway environment variable documentation
* Document Parser Service initial FastAPI structure
* Document Parser Service health check endpoint
* Document Parser Service PDF parsing endpoint
* Document Parser Service API contract documentation
* Document Parser Service environment variable documentation

### Not Implemented Yet

* Frontend Next.js application
* API Gateway routing to Document Parser Service
* Agent Service
* LangGraph workflow
* Gemini integration
* Embedding-based skill matching
* Fit score calculation
* Supabase integration
* Result persistence
* Session status tracking
* End-to-end `/analyze` flow

---

## MVP Success Criteria

The MVP is considered successful when the following vertical slice works:

```text
User uploads CV PDF and enters JD text
→ Frontend sends request to API Gateway
→ API Gateway sends CV PDF to Document Parser Service
→ Document Parser Service returns CV text
→ Agent Service analyzes CV text against JD text
→ System returns fit score, matched skills, missing skills, suggestions, and conditional output
→ Frontend displays the result
```

The first complete MVP does not need authentication, payment, dashboard, OCR, or advanced history.
