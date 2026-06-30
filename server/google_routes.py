import logging
import secrets
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .config import get_settings
from .crypto import encrypt_token
from .database import get_db
from .deps import get_current_user
from .models import EmailConnection, User
from .google_client import fetch_email_address, fetch_messages, get_valid_google_token

log = logging.getLogger(__name__)
settings = get_settings()

auth_router = APIRouter(prefix="/auth/google", tags=["oauth-google"])
google_router = APIRouter(prefix="/email", tags=["google"])

# ─── Auth Routes ─────────────────────────────────────────────────────────────

@auth_router.get("/login")
def google_login(request: Request, user: User = Depends(get_current_user)):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be configured"
        )

    # 1. Generate CSRF state
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state

    # 2. Build Google authorization URL
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_callback_url,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    
    url = str(httpx.URL(auth_url).copy_with(params=params))
    return RedirectResponse(url)


@auth_router.get("/callback")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 1. Validate CSRF state
    expected_state = request.session.pop("google_oauth_state", None)
    if not expected_state or not secrets.compare_digest(expected_state, state):
        log.warning("google_callback: session state mismatch for user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing CSRF state"
        )

    # 2. Exchange code for token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "redirect_uri": settings.google_callback_url,
                "grant_type": "authorization_code",
            },
        )
        if not resp.is_success:
            log.error("Google token exchange failed: %s", resp.text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code",
            )
            
        data = resp.json()
        access_token = data["access_token"]
        refresh_token = data.get("refresh_token")
        expires_in = data.get("expires_in", 3599)

        # 3. Fetch user email
        try:
            email_address = await fetch_email_address(client, access_token)
        except Exception as e:
            log.exception("Failed to fetch email address")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch Google user info",
            )

    # 4. Save/Update connection
    token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    
    conn = db.query(EmailConnection).filter(EmailConnection.user_id == user.id).first()
    if conn:
        conn.email_address = email_address
        conn.access_token_encrypted = encrypt_token(access_token)
        if refresh_token:
            conn.refresh_token_encrypted = encrypt_token(refresh_token)
        conn.token_expiry = token_expiry
        conn.connected_at = datetime.now(timezone.utc)
    else:
        conn = EmailConnection(
            user_id=user.id,
            email_address=email_address,
            access_token_encrypted=encrypt_token(access_token),
            refresh_token_encrypted=encrypt_token(refresh_token) if refresh_token else None,
            token_expiry=token_expiry,
        )
        db.add(conn)
        
    db.commit()
    log.info("Updated Google EmailConnection for user_id=%s email=%s", user.id, email_address)

    return RedirectResponse("/")


@auth_router.post("/disconnect")
def google_disconnect(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conn = db.query(EmailConnection).filter(EmailConnection.user_id == user.id).first()
    if conn:
        db.delete(conn)
        db.commit()
        log.info("Deleted EmailConnection for user_id=%s", user.id)
    return {"connected": False}


# ─── Data Routes ─────────────────────────────────────────────────────────────

@google_router.get("/status")
def google_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conn = db.query(EmailConnection).filter(EmailConnection.user_id == user.id).first()
    if not conn:
        return {"connected": False, "email_address": None}
    return {"connected": True, "email_address": conn.email_address}


@google_router.get("/messages")
async def google_messages(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conn = db.query(EmailConnection).filter(EmailConnection.user_id == user.id).first()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "not_connected"}
        )

    try:
        token = await get_valid_google_token(db, conn)
    except HTTPException:
        raise 
    
    try:
        messages = await fetch_messages(token)
    except HTTPException as e:
        if e.status_code == 401:
            db.delete(conn)
            db.commit()
        raise

    return {"messages": messages}
