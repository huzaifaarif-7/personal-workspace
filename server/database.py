"""Database engine, session factory, and declarative Base for the workspace dashboard.

Uses a local SQLite file (dashboard.db) so there are no external services needed
during development.  Switch DATABASE_URL to PostgreSQL for production without
touching any model or dependency code.

Usage in a route:
    from server.database import get_db
    from sqlalchemy.orm import Session
    from fastapi import Depends

    @router.get("/example")
    def example(db: Session = Depends(get_db)):
        ...
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

# File-based SQLite at the repo root.  The path is relative to wherever the
# process is started (normally the repo root when running uvicorn).
# On Vercel, VERCEL env var is automatically set; /tmp is the only writable dir.
# Check for Vercel Postgres or Supabase
if os.environ.get("POSTGRES_URL"):
    db_url = os.environ.get("POSTGRES_URL")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL = db_url
elif os.environ.get("DATABASE_URL"):
    db_url = os.environ.get("DATABASE_URL")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL = db_url
elif os.environ.get("VERCEL") or os.environ.get("AWS_EXECUTION_ENV") or os.path.exists("/var/task"):
    # Serverless environments (Vercel/AWS Lambda) have a read-only filesystem except for /tmp
    DATABASE_URL = "sqlite:////tmp/dashboard.db"
else:
    DATABASE_URL = "sqlite:///./dashboard.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# `check_same_thread=False` is required for SQLite when the same connection
# object may be used across threads (FastAPI uses a thread-pool executor).
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # Echo SQL to stdout — flip to True when troubleshooting queries.
    echo=False,
)

# All database sessions are created from this factory.
# autocommit=False → you must call db.commit() explicitly (safer default).
# autoflush=False  → prevents implicit flushes before every query.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every ORM model inherits from Base so SQLAlchemy can track them collectively
# and create/drop all tables via Base.metadata.create_all(engine).
Base = declarative_base()


def _init_db() -> None:
    """Create all ORM tables at import time.

    IMPORTANT: On Vercel serverless, @app.on_event('startup') handlers are NOT
    guaranteed to run before the first request.  Tables must be created here, at
    module level, so they exist for every cold-start invocation.

    Import models inside this function to avoid circular imports — models.py
    imports Base from this module, so importing models at the top of this module
    would create a cycle.  The local import is fine; Python caches modules.
    """
    import logging
    import server.models  # noqa: F401 — registers User, GitHubConnection, EmailConnection
    Base.metadata.create_all(bind=engine)
    logging.getLogger("workspace").info(
        "[database] Tables verified / created at: %s", DATABASE_URL
    )


_init_db()


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
