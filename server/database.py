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
if os.environ.get("VERCEL"):
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/dashboard.db")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dashboard.db")



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
