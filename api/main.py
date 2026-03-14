import logging

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import PlainTextResponse

from api.routers.analyze import router as analyze_router
from utils.config import get_settings
from utils.logging import configure_logging
from utils.security import redact_phi
from utils.tracing import ensure_request_id

settings = get_settings()
configure_logging(settings.log_level)
LOGGER = logging.getLogger("api")

app = FastAPI(title="Multimodal Medical AI", version="0.1.0")
app.include_router(analyze_router, prefix=settings.api_prefix)


@app.middleware("http")
async def request_audit_middleware(request: Request, call_next):
    request_id = ensure_request_id()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    user_agent = request.headers.get("user-agent", "")
    # Avoid logging payload content; redact free-text header values for safety.
    LOGGER.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "user_agent": redact_phi(user_agent),
        },
    )
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> str:
    # Prometheus-ready endpoint placeholder.
    return "app_up 1\n"
