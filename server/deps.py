"""FastAPI dependencies for the workspace dashboard.

Contains reusable `Depends(...)` callables that routes can inject.

Current dependencies
--------------------
get_current_user
    Lightweight single-workspace-user identity using a signed session cookie.
    No login page required — a User row is auto-created on the first visit and
    its id is persisted in the session.  Full OAuth-based auth can be layered
    on top later without changing the schema.

Usage in a route::

    from fastapi import Depends
    from sqlalchemy.orm import Session
    from starlette.requests import Request

    from server.database import get_db
    from server.deps import get_current_user
    from server.models import User

    @router.get("/me")
    def me(user: User = Depends(get_current_user)):
        return {"id": user.id, "name": user.display_name}

    # If you also need the DB session in the same route, declare it explicitly:
    @router.get("/me/connections")
    def connections(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ...
"""
import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request

from .database import get_db
from .models import User

log = logging.getLogger("workspace")


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Return the workspace User for this session, creating one if needed.

    Session cookie lifecycle
    ~~~~~~~~~~~~~~~~~~~~~~~~
    1. First visit (no cookie / no "user_id" key):
       - Creates a new User row with a default display_name.
       - Stores `user.id` in `request.session["user_id"]`.
       - Returns the new User.

    2. Subsequent visits (cookie present, "user_id" key exists):
       - Loads the User from the database by id.
       - Returns the existing User.
       - Raises HTTP 500 if the id in the session doesn't match any row
         (data-corruption guard — should never happen in normal operation).

    The session cookie is signed by Starlette's SessionMiddleware using
    SESSION_SECRET_KEY, so clients cannot forge or tamper with the user_id.

    Args:
        request: Injected by FastAPI from the incoming HTTP request.
        db:      Database session injected via get_db().

    Returns:
        The User ORM model instance for the current session.

    Raises:
        HTTPException(500): If a session user_id exists but has no matching
            User row (indicates DB corruption or manual session manipulation).
    """
    user_id: int | None = request.session.get("user_id")

    if user_id is None:
        # ── First visit ──────────────────────────────────────────────────────
        # No session yet.  Auto-create a User so routes always have a real
        # identity to work with, even before any login flow is built.
        user = User(display_name="Workspace User")
        db.add(user)
        db.commit()
        db.refresh(user)               # populate user.id from the DB
        request.session["user_id"] = user.id
        log.info("Created new workspace user id=%d", user.id)
        return user

    # ── Returning visit ──────────────────────────────────────────────────────
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        # The session references a user that no longer exists in the DB.
        # Clear the stale session so the next request creates a fresh user.
        request.session.clear()
        log.error(
            "Session contained unknown user_id=%d — session cleared.", user_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Session references a user that no longer exists. "
                "Please refresh the page to start a new session."
            ),
        )

    return user
