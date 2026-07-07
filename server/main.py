"""Workspace — FastAPI app (single-domain Vercel deployment).

Exposed to Vercel via /api/index.py. Only /api/* reaches this function, so docs
and health live under /api too. Locally: uvicorn server.main:app --reload

Import note: All server modules are flat in server/ — there are no routers/ or
services/ subdirectories on disk.  Only the four modules that define an APIRouter
(oauth, dashboard, calendar, email) are registered below; the others (slack,
github, calendly, assistant, google) are pure service/client modules.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .database import Base, engine                        # tables created at import time in database._init_db()
from .github_routes import (                              # new GitHub OAuth + data routes
    auth_router as gh_auth_router,
    github_router as gh_github_router,
)
from .google_routes import (                              # new Google OAuth + data routes
    auth_router as go_auth_router,
    google_router as go_google_router,
)
from .auth_routes import (                                # new User Auth routes
    auth_router as local_auth_router,
    user_router as local_user_router,
)
# Route modules — only import modules that define `router = APIRouter(...)`
from . import dashboard, calendar
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title=settings.app_name, version="2.0.0",
    description="Unified productivity dashboard — Slack, Calendar, Calendly, GitHub, "
                "Gmail and an AI assistant. Live data with graceful demo fallback.",
    docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, StarletteHTTPException):
        content = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
        return JSONResponse(status_code=exc.status_code, content=content)
    if isinstance(exc, RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    logging.getLogger("workspace").exception("Unhandled exception:")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)}
    )


# ── Middleware ───────────────────────────────────────────────────────────────
# SessionMiddleware MUST be added before CORSMiddleware so that session data
# is available to any middleware or route that runs after it.
# The secret key signs the cookie — rotating it invalidates all existing sessions.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    # https_only=True in production (set via env / reverse proxy)
    https_only=False,
    same_site="lax",
)

# Same-origin in production, so CORS is mostly a no-op; kept for local two-server dev.
_origins = {settings.frontend_url, "http://localhost:5173", "http://localhost:3000"}
_origins |= {o.strip() for o in settings.extra_cors.split(",") if o.strip()}
app.add_middleware(
    CORSMiddleware, allow_origins=list(_origins),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
# Legacy routes (dashboard aggregate, calendar)
for r in (dashboard, calendar):
    app.include_router(r.router, prefix=settings.api_prefix)

# GitHub OAuth + data routes
app.include_router(gh_auth_router,   prefix=settings.api_prefix)
app.include_router(gh_github_router, prefix=settings.api_prefix)

# Google OAuth + data routes
app.include_router(go_auth_router,   prefix=settings.api_prefix)
app.include_router(go_google_router, prefix=settings.api_prefix)

# User Auth routes
app.include_router(local_auth_router, prefix=settings.api_prefix)
app.include_router(local_user_router, prefix=settings.api_prefix)


# ── Startup ───────────────────────────────────────────────────────────────────
# NOTE: Base.metadata.create_all() is called at module-import time in
# server/database.py (_init_db).  On Vercel serverless, @app.on_event("startup")
# handlers are NOT guaranteed to fire before the first request arrives, so we
# must not rely on them for table creation.  No startup event handler needed.


@app.get("/api/health", tags=["meta"])
def health():
    from . import data
    return {"status": "ok", "service": settings.app_name, "connected": data.status()}
