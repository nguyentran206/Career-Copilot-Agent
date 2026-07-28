import json
import logging
import re
from contextvars import ContextVar
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request


REQUEST_ID_HEADER = "X-Request-ID"
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
request_id_context: ContextVar[str] = ContextVar("request_id", default="unknown")
logger = logging.getLogger("career_copilot.requests")


def get_request_id() -> str:
    return request_id_context.get()


def log_event(event: str, **fields: object) -> None:
    logger.info(json.dumps({"event": event, **fields}, ensure_ascii=True))


def setup_request_context(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = incoming if _SAFE_REQUEST_ID.fullmatch(incoming) else str(uuid4())
        request.state.request_id = request_id
        token = request_id_context.set(request_id)
        started = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            if request.url.path.startswith(("/api/v1/analyze", "/api/v1/session/")):
                response.headers["Cache-Control"] = "no-store, max-age=0"
            return response
        finally:
            log_event(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=round((perf_counter() - started) * 1000, 2),
            )
            request_id_context.reset(token)
