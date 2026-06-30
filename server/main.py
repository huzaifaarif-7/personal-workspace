"""Huzaifa's Workspace — FastAPI app (single-domain Vercel deployment).

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
from .database import Base, engine                        # for create_all on startup
from .github_routes import (                              # new GitHub OAuth + data routes
    auth_router as gh_auth_router,
    github_router as gh_github_router,
)
from .google_routes import (                              # new Google OAuth + data routes
    auth_router as go_auth_router,
    google_router as go_google_router,
)
# Route modules — only import modules that define `router = APIRouter(...)`
from . import dashboard, calendar

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title=settings.app_name, version="2.0.0",
    description="Unified productivity dashboard — Slack, Calendar, Calendly, GitHub, "
                "Gmail and an AI assistant. Live data with graceful demo fallback.",
    docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json",
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


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def _create_tables() -> None:
    """Create all ORM tables on startup if they don't exist yet.

    Using create_all() is appropriate while there is no Alembic migration
    history.  Once you introduce Alembic, remove this call and run
    `alembic upgrade head` instead.

    Importing models here (not at module level) avoids circular imports
    while still ensuring all Table objects are registered on Base.metadata
    before create_all() is called.
    """
    import server.models  # noqa: F401 — registers User, GitHubConnection, EmailConnection
    Base.metadata.create_all(bind=engine)
    logging.getLogger("workspace").info(
        "Database tables verified / created (dashboard.db)"
    )


@app.get("/api/health", tags=["meta"])
def health():
    from . import data
    return {"status": "ok", "service": settings.app_name, "connected": data.status()}
