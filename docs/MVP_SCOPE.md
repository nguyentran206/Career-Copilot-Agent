# Career Copilot Agent - MVP Scope

## Goal
Build an AI agent that analyzes a CV against a Job Description and returns a fit score, missing skills, CV improvement suggestions, and a learning roadmap.

## Input
- CV file in PDF format
- Job Description text

## Output
- Parsed CV information
- Parsed JD requirements
- Fit score from 0 to 100
- Matched skills
- Missing skills
- CV improvement suggestions
- Learning roadmap

## In MVP
- PDF parsing
- JD parsing
- LangGraph agent pipeline
- Embedding-based skill matching
- FastAPI endpoint
- Basic frontend upload form

## Not in MVP
- Authentication
- User dashboard
- Payment
- Advanced analytics
- Beautiful PDF report
- Multi-user history