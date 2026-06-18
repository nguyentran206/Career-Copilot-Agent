# Architecture Draft

## Deployment
- Frontend: Vercel
- Backend: AWS
- Database: Supabase PostgreSQL
- Storage: Supabase Storage
- AI API: Gemini API

## Main Flow
1. User uploads CV PDF and enters Job Description.
2. Frontend sends file and JD text to FastAPI backend.
3. Backend extracts text from CV PDF.
4. LangGraph agent parses CV and JD.
5. Embedding model calculates similarity between CV skills and JD skills.
6. Agent generates suggestions and roadmap.
7. Backend saves result to Supabase.
8. Frontend displays analysis result.

## Agent Nodes
- parse_cv_node
- parse_jd_node
- match_skills_node
- suggest_improvements_node
- generate_roadmap_node