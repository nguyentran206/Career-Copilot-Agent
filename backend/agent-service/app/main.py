from fastapi import FastAPI

from app.api.v1.routes import router
from app.core.config import settings
from app.core.request_context import setup_request_context


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)
setup_request_context(app)

app.include_router(router, prefix=settings.api_prefix)
