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
4. LangGraph agent parses the CV and JD into structured data.
5. Agent evaluates job fit score and identifies missing or weak skills.
6. Agent decides the best response strategy based on fit score, skill gaps, and CV quality.
7. Agent conditionally routes the workflow:
   - High fit: generate cover letter only.
   - Medium fit: suggest CV improvements and generate cover letter.
   - Low fit: suggest improvements and generate a learning roadmap.
8. Backend saves the analysis result to Supabase.
9. Frontend displays the personalized result.

## Agent Nodes
- parse_cv_node
- parse_jd_node
- match_skills_node
- suggest_improvements_node
- generate_roadmap_node