import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session

from .config import get_settings
from .crypto import encrypt_token
from .database import get_db
from .deps import get_current_user
from .models import SlackConnection, User

log = logging.getLogger("workspace.slack")
settings = get_settings()

SLACK_SCOPES = "search:read,users:read,channels:history,im:history,im:read,mpim:read,mpim:history"

auth_router = APIRouter(prefix="/auth/slack", tags=["slack-auth"])
slack_router = APIRouter(prefix="/slack", tags=["slack"])


def _frontend_redirect(ok: bool) -> RedirectResponse:
    return RedirectResponse(
        f"{settings.frontend_url}/?connected=slack&ok={int(ok)}"
    )


@auth_router.get("/login", summary="Start Slack OAuth flow")
def slack_login(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RedirectResponse:
    if not settings.slack_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SLACK_CLIENT_ID is not configured",
        )
    if not settings.slack_redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SLACK_REDIRECT_URI is not configured",
        )

    state = secrets.token_urlsafe(32)
    request.session["slack_oauth_state"] = state

    log.info("Slack OAuth login initiated for user_id=%d", user.id)

    auth_url = (
        "https://slack.com/oauth/v2/authorize"
        f"?client_id={settings.slack_client_id}"
        f"&user_scope={SLACK_SCOPES}"
        f"&redirect_uri={settings.slack_redirect_uri}"
        f"&state={state}"
    )
    return RedirectResponse(auth_url)


@auth_router.get("/callback", summary="Slack OAuth callback")
async def slack_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RedirectResponse:
    if error:
        log.warning("Slack OAuth denied: %s", error)
        return _frontend_redirect(ok=False)

    if not code or not state:
        log.warning("Slack callback missing code or state param")
        return _frontend_redirect(ok=False)

    stored_state = request.session.pop("slack_oauth_state", None)

    if not stored_state or stored_state != state:
        log.warning("Slack OAuth CSRF state mismatch")
        return _frontend_redirect(ok=False)

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": settings.slack_client_id,
                "client_secret": settings.slack_client_secret,
                "code": code,
                "redirect_uri": settings.slack_redirect_uri,
            },
        )
        data = res.json()
        if not data.get("ok"):
            log.error("Slack token exchange failed: %s", data.get("error"))
            return _frontend_redirect(ok=False)

        authed_user = data.get("authed_user", {})
        raw_token = authed_user.get("access_token")
        slack_user_id = authed_user.get("id")

        if not raw_token or not slack_user_id:
            log.error("Slack OAuth missing access_token or user_id")
            return _frontend_redirect(ok=False)

    encrypted = encrypt_token(raw_token)
    conn = (
        db.query(SlackConnection)
        .filter(SlackConnection.user_id == user.id)
        .first()
    )

    if conn:
        conn.slack_user_id = slack_user_id
        conn.access_token_encrypted = encrypted
        log.info("Updated SlackConnection for user_id=%d", user.id)
    else:
        conn = SlackConnection(
            user_id=user.id,
            slack_user_id=slack_user_id,
            access_token_encrypted=encrypted,
        )
        db.add(conn)
        log.info("Created SlackConnection for user_id=%d", user.id)

    db.commit()
    return _frontend_redirect(ok=True)


@auth_router.post("/disconnect", summary="Disconnect Slack account")
def slack_disconnect(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    conn = (
        db.query(SlackConnection)
        .filter(SlackConnection.user_id == user.id)
        .first()
    )
    if conn:
        db.delete(conn)
        db.commit()
        log.info("Deleted SlackConnection for user_id=%d", user.id)

    return {"connected": False}


@slack_router.get("/status", summary="Slack connection status")
def slack_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    conn = (
        db.query(SlackConnection)
        .filter(SlackConnection.user_id == user.id)
        .first()
    )
    return {
        "connected": conn is not None,
    }
