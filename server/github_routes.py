"""GitHub OAuth and data routes for the workspace dashboard.

Exposes five endpoints across two APIRouter objects:

    auth_router  (prefix /auth/github)  — OAuth flow + disconnect
    github_router (prefix /github)      — status + data summary

Both are registered in main.py under the /api prefix, giving final paths:
    GET  /api/auth/github/login
    GET  /api/auth/github/callback
    POST /api/auth/github/disconnect
    GET  /api/github/status
    GET  /api/github/summary

Design notes
------------
- CSRF protection: a random `state` token is stored in the session before the
  GitHub redirect and verified when GitHub calls back. Mismatch → rejected.
- Token storage: the raw access_token is encrypted via server.crypto before
  being written to GitHubConnection. It is never logged or returned in any
  response.
- Upsert pattern: if a GitHubConnection already exists for this user it is
  updated in-place rather than deleted+recreated, preserving the row's `id`.
- Async: /summary uses an async route handler so asyncio.gather() in
  github_client.fetch_summary() actually runs the four API calls concurrently.
"""
import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .config import get_settings
from .crypto import decrypt_token, encrypt_token
from .database import get_db
from .deps import get_current_user
from . import github_client
from .github_client import RateLimitedError, TokenRevokedError
from .models import GitHubConnection, User

log = logging.getLogger("workspace.github")
settings = get_settings()

# ── Scopes we request from GitHub ───────────────────────────────────────────
# read:user       — username + profile info
# notifications   — read/write notification state
# repo            — full repo access (required for private repo activity)
GITHUB_SCOPES = "read:user notifications repo"

# ── Routers ──────────────────────────────────────────────────────────────────
# Two separate routers so each can carry its own prefix.
# Both get registered in main.py under settings.api_prefix (/api).
auth_router = APIRouter(prefix="/auth/github", tags=["github-auth"])
github_router = APIRouter(prefix="/github", tags=["github"])


# ---------------------------------------------------------------------------
# Helper: redirect back to the frontend homepage
# ---------------------------------------------------------------------------

def _frontend_redirect(ok: bool) -> RedirectResponse:
    """Build a RedirectResponse to the frontend with a connection status flag."""
    return RedirectResponse(
        f"{settings.frontend_url}/?connected=github&ok={int(ok)}"
    )


# ---------------------------------------------------------------------------
# GET /api/auth/github/login
# ---------------------------------------------------------------------------

@auth_router.get("/login", summary="Start GitHub OAuth flow")
def github_login(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RedirectResponse:
    """Generate a CSRF state token and redirect to GitHub's authorisation page.

    IMPORTANT: get_current_user is injected here so that the session cookie
    already contains `user_id` before the GitHub redirect.  Without this,
    the login response sets a cookie with only the CSRF state, and when GitHub
    redirects back to /callback, get_current_user sees no user_id and creates a
    brand-new User row — causing the callback and all subsequent API calls to
    resolve to different users (session mismatch → 401 not_connected).

    The `state` value is a cryptographically random URL-safe string stored in
    the signed session cookie.  GitHub echoes it back on the callback so we can
    verify the request originated from us (CSRF protection).

    Raises:
        HTTPException(500): If GITHUB_CLIENT_ID or GITHUB_REDIRECT_URI is not
            configured in the environment.
    """
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GITHUB_CLIENT_ID is not configured",
        )
    if not settings.github_redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GITHUB_REDIRECT_URI is not configured",
        )

    # Generate and persist the CSRF state in the session
    state = secrets.token_urlsafe(32)
    request.session["github_oauth_state"] = state

    # DIAGNOSTIC: log what the session contains when the login is initiated
    raw_cookie = request.cookies.get("session", "")
    log.info(
        "[session] github_login: user_id=%d  cookie_present=%s  cookie_prefix=%r  "
        "session_keys=%s",
        user.id,
        bool(raw_cookie),
        raw_cookie[:20] if raw_cookie else None,
        list(request.session.keys()),
    )

    log.info("GitHub OAuth login initiated for user_id=%d (state stored in session)", user.id)

    auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_redirect_uri}"
        f"&scope={GITHUB_SCOPES.replace(' ', '%20')}"
        f"&state={state}"
    )
    return RedirectResponse(auth_url)


# ---------------------------------------------------------------------------
# GET /api/auth/github/callback
# ---------------------------------------------------------------------------

@auth_router.get("/callback", summary="GitHub OAuth callback")
async def github_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RedirectResponse:
    """Handle the OAuth callback from GitHub.

    Steps:
    1. Validate `code` and `state` are present; reject on error param.
    2. Pop the stored state from the session (clears it regardless of outcome).
    3. Compare stored vs returned state — mismatch → CSRF, redirect failure.
    4. Exchange the authorisation code for an access token via GitHub API.
    5. Fetch the GitHub username with the new token.
    6. Encrypt the token and upsert a GitHubConnection for the current user.
    7. Redirect to the frontend dashboard with ?connected=github&ok=1.

    Args:
        request: Starlette Request (for session access).
        code:    GitHub authorisation code (query param).
        state:   CSRF state echoed by GitHub (query param).
        error:   Error string sent by GitHub on denial (query param).
        db:      Database session dependency.
        user:    Current workspace user dependency.
    """
    # ── 1. Handle explicit GitHub error (user denied, etc.) ─────────────────
    if error:
        log.warning("GitHub OAuth denied by user or GitHub: %s", error)
        return _frontend_redirect(ok=False)

    if not code or not state:
        log.warning("GitHub callback missing code or state param")
        return _frontend_redirect(ok=False)

    # ── 2. Pop CSRF state from session (always clear after one use) ──────────
    stored_state = request.session.pop("github_oauth_state", None)

    # ── 3. CSRF verification ─────────────────────────────────────────────────
    if not stored_state or stored_state != state:
        log.warning(
            "GitHub OAuth CSRF state mismatch — possible CSRF attempt "
            "(stored=%r, received=%r)", stored_state, state
        )
        return _frontend_redirect(ok=False)

    # ── 4. Exchange code for access token ────────────────────────────────────
    try:
        raw_token = await github_client.exchange_code(
            code=code,
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            redirect_uri=settings.github_redirect_uri,
        )
    except Exception as exc:
        log.error("GitHub token exchange failed: %s", exc)
        return _frontend_redirect(ok=False)

    # ── 5. Fetch the GitHub username ─────────────────────────────────────────
    try:
        import httpx as _httpx
        async with _httpx.AsyncClient(timeout=10) as client:
            username = await github_client.get_username(client, raw_token)
    except Exception as exc:
        log.error("GitHub /user fetch failed after token exchange: %s", exc)
        return _frontend_redirect(ok=False)

    # ── 6. Encrypt + upsert GitHubConnection ─────────────────────────────────
    encrypted = encrypt_token(raw_token)
    conn = (
        db.query(GitHubConnection)
        .filter(GitHubConnection.user_id == user.id)
        .first()
    )

    if conn:
        # Update the existing connection (preserves row id + connected_at)
        conn.github_username = username
        conn.access_token_encrypted = encrypted
        conn.scopes = GITHUB_SCOPES
        log.info(
            "Updated GitHubConnection for user_id=%d username=%s",
            user.id, username,
        )
    else:
        conn = GitHubConnection(
            user_id=user.id,
            github_username=username,
            access_token_encrypted=encrypted,
            scopes=GITHUB_SCOPES,
        )
        db.add(conn)
        log.info(
            "Created GitHubConnection for user_id=%d username=%s",
            user.id, username,
        )

    db.commit()

    # DIAGNOSTIC: log which user the connection was saved to
    log.info(
        "[session] github_callback done: user_id=%d username=%r  "
        "cookie_prefix=%r",
        user.id,
        username,
        request.cookies.get("session", "")[:20],
    )

    # ── 7. Redirect to frontend ────────────────────────────────────────────────
    return _frontend_redirect(ok=True)


# ---------------------------------------------------------------------------
# POST /api/auth/github/disconnect
# ---------------------------------------------------------------------------

@auth_router.post("/disconnect", summary="Disconnect GitHub account")
def github_disconnect(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Delete the current user's GitHubConnection row.

    Safe to call even if no connection exists (idempotent).

    Returns:
        {"connected": false}
    """
    conn = (
        db.query(GitHubConnection)
        .filter(GitHubConnection.user_id == user.id)
        .first()
    )
    if conn:
        db.delete(conn)
        db.commit()
        log.info("Deleted GitHubConnection for user_id=%d", user.id)

    return {"connected": False}


# ---------------------------------------------------------------------------
# GET /api/github/status
# ---------------------------------------------------------------------------

@github_router.get("/status", summary="GitHub connection status")
def github_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Return whether the current user has a connected GitHub account.

    The access token is never included in the response — only the connection
    state and username are exposed.

    Returns:
        {"connected": true, "username": "octocat"}
        {"connected": false, "username": null}
    """
    conn = (
        db.query(GitHubConnection)
        .filter(GitHubConnection.user_id == user.id)
        .first()
    )
    return {
        "connected": conn is not None,
        "username": conn.github_username if conn else None,
    }


# ---------------------------------------------------------------------------
# GET /api/github/summary
# ---------------------------------------------------------------------------

@github_router.get("/summary", summary="GitHub dashboard summary")
async def github_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Fetch a combined GitHub summary for the current user.

    Makes four concurrent GitHub API calls (notifications, PRs, issues,
    activity) and returns them as a single JSON payload so the frontend
    only needs one request.

    Returns:
        {
            "notifications":   [{id, repo, title, reason, unread, updated_at, url}, ...],
            "pull_requests":   [{id, repo, title, url, updated_at}, ...],
            "assigned_issues": [{id, repo, title, url, updated_at}, ...],
            "recent_activity": [{type, repo, summary, created_at}, ...],
        }

    Raises:
        HTTPException(401): No GitHubConnection exists for this user
            (body: {"error": "not_connected"}).
        HTTPException(401): The stored token has been revoked or expired —
            the connection is deleted from DB
            (body: {"error": "token_invalid"}).
        HTTPException(429): GitHub rate limit is exhausted
            (body: {"error": "rate_limited", "reset_at": "<iso-datetime>"}).
    """
    # ── Require an existing connection ───────────────────────────────────────
    conn = (
        db.query(GitHubConnection)
        .filter(GitHubConnection.user_id == user.id)
        .first()
    )
    if not conn:
        log.warning(
            "github/summary: no GitHubConnection for user_id=%d — "
            "session may not match the user who completed OAuth",
            user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "not_connected"},
        )

    # ── Decrypt the stored token ──────────────────────────────────────────────
    # decrypt_token raises cryptography.fernet.InvalidToken if the ciphertext
    # is corrupt; let that propagate as a 500 (should never happen in practice).
    token = decrypt_token(conn.access_token_encrypted)

    # Debug: log non-secret token markers so we can verify the pipeline
    # without ever exposing the full token value.
    log.debug(
        "github/summary: user_id=%d username=%r "
        "encrypted_prefix=%r decrypted_prefix=%r",
        user.id,
        conn.github_username,
        conn.access_token_encrypted[:10],
        token[:8],
    )

    # ── Fetch summary concurrently ────────────────────────────────────────────
    try:
        summary = await github_client.fetch_summary(
            token=token,
            username=conn.github_username,
        )
    except TokenRevokedError:
        # Token is no longer valid — purge the connection so the frontend
        # knows to prompt reconnect on the next status check.
        log.warning(
            "GitHub token invalid for user_id=%d username=%r — deleting connection. "
            "Encrypted prefix: %r  Decrypted prefix: %r",
            user.id,
            conn.github_username,
            conn.access_token_encrypted[:10],
            token[:8],
        )
        db.delete(conn)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "token_invalid"},
        )
    except RateLimitedError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limited", "reset_at": exc.reset_at},
        )

    return summary
