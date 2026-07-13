from fastapi import APIRouter

from app.modules.health.routes import router as health_router
from app.modules.analyze.routes import router as analyze_router
from app.modules.session.routes import router as session_router


api_router = APIRouter()

api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    analyze_router,
    tags=["Analyze"],
)

api_router.include_router(
    session_router,
    tags=["Session"],
)
