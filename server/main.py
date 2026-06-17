"""Huzaifa's Workspace — FastAPI app (single-domain Vercel deployment).

Exposed to Vercel via /api/index.py. Only /api/* reaches this function, so docs
and health live under /api too. Locally: uvicorn server.main:app --reload
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import (assistant, auth, calendar, calendly, dashboard,
                      email, github, oauth, slack)

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title=settings.app_name, version="2.0.0",
    description="Unified productivity dashboard — Slack, Calendar, Calendly, GitHub, "
                "Gmail and an AI assistant. Live data with graceful demo fallback.",
    docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json",
)

# Same-origin in production, so CORS is mostly a no-op; kept for local two-server dev.
_origins = {settings.frontend_url, "http://localhost:5173", "http://localhost:3000"}
_origins |= {o.strip() for o in settings.extra_cors.split(",") if o.strip()}
app.add_middleware(
    CORSMiddleware, allow_origins=list(_origins),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

for r in (auth, oauth, dashboard, slack, calendar, calendly, github, email, assistant):
    app.include_router(r.router, prefix=settings.api_prefix)


@app.get("/api/health", tags=["meta"])
def health():
    from .services import data
    return {"status": "ok", "service": settings.app_name, "connected": data.status()}
