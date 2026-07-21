"""Database engine, session factory, and declarative Base for the workspace dashboard.

Backed by Supabase Postgres — the schema is pre-applied and the app only
reads/writes data; it never creates or alters tables.

Usage in a route:
    from server.database import get_db
    from sqlalchemy.orm import Session
    from fastapi import Depends

    @router.get("/example")
    def example(db: Session = Depends(get_db)):
        ...
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

log = logging.getLogger("workspace")

# ── Connection URL ────────────────────────────────────────────────────────────
# Reads DATABASE_URL (or POSTGRES_URL as a fallback alias).
# Supabase provides a postgresql://... connection string.
# The legacy "postgres://" scheme is normalised to "postgresql://" for SQLAlchemy.

_raw_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
if not _raw_url:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Add the Supabase connection string to your .env file."
    )
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL: str = _raw_url

# ── Engine ────────────────────────────────────────────────────────────────────
# Pool settings tuned for a long-running server connecting to Supabase Postgres.
# pool_pre_ping performs a lightweight health-check before handing a connection
# from the pool to a request, which prevents errors after idle periods.
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,   # recycle connections every 30 min — avoids stale connections
    pool_pre_ping=True,  # test connection health before use
    echo=False,          # flip to True when troubleshooting slow queries
)

# ── Session factory ───────────────────────────────────────────────────────────
# autocommit=False → routes must call db.commit() explicitly (safer default).
# autoflush=False  → prevents implicit flushes before every query.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative Base ──────────────────────────────────────────────────────────
# All ORM models inherit from Base.  create_all() is intentionally NOT called —
# the schema already exists in Supabase and must not be modified by the app.
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session per request.

    Opens a new session, yields it to the route handler, and guarantees
    the session is closed when the request finishes — even on exceptions.

    Typical use::

        @router.get("/something")
        def handler(db: Session = Depends(get_db)):
            users = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
