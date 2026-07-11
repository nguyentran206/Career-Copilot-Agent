from fastapi import APIRouter

from app.core.config import settings
from app.schemas.analysis import AgentAnalyzeRequest, AgentAnalyzeResponse
from app.services.analyzer import analyze_cv_against_jd


router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "agent-service",
        "version": settings.app_version,
    }


@router.post("/analyze", response_model=AgentAnalyzeResponse)
def analyze(request: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
    return analyze_cv_against_jd(request)