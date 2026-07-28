from fastapi import FastAPI

from app.api.v1.routes import api_router
from app.core.config import settings
from app.core.cors import setup_cors
from app.core.request_context import setup_request_context


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API Gateway for Career Copilot microservices.",
    )

    setup_cors(app)
    setup_request_context(app)

    app.include_router(
        api_router,
        prefix=settings.api_prefix,
    )

    return app


app = create_app()
