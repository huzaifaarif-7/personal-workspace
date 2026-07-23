import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .config import get_settings
from .crypto import encrypt_token, decrypt_token
from .models import EmailConnection

log = logging.getLogger(__name__)
settings = get_settings()

GOOGLE_API_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GMAIL_API_URL = "https://gmail.googleapis.com/gmail/v1"
GCAL_API_URL = "https://www.googleapis.com/calendar/v3"

def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

async def fetch_email_address(client: httpx.AsyncClient, token: str) -> str:
    resp = await client.get(GOOGLE_API_URL, headers=_headers(token))
    resp.raise_for_status()
    return resp.json()["email"]

async def get_valid_google_token(db: Session, conn: EmailConnection) -> str:
    """Returns a valid access token, refreshing if necessary."""
    # SQLite often returns datetime as naive even if stored as aware.
    # We must ensure it has tzinfo=timezone.utc before comparing.
    expiry = conn.token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if expiry > now:
        return decrypt_token(conn.access_token_encrypted)

    if not conn.refresh_token_encrypted:
        # No refresh token available and access token expired
        db.delete(conn)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "token_invalid", "reason": "expired_no_refresh"}
        )

    refresh_token = decrypt_token(conn.refresh_token_encrypted)
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }
        )
        
        if not resp.is_success:
            log.warning("Failed to refresh Google token for user %s: %s", conn.user_id, resp.text)
            db.delete(conn)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "token_invalid", "reason": "refresh_failed"}
            )
            
        data = resp.json()
        new_token = data["access_token"]
        expires_in = data.get("expires_in", 3599)
        
        conn.access_token_encrypted = encrypt_token(new_token)
        conn.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        # Google sometimes issues a new refresh token
        if "refresh_token" in data:
            conn.refresh_token_encrypted = encrypt_token(data["refresh_token"])
            
        db.commit()
        return new_token

async def _fetch_message_metadata(client: httpx.AsyncClient, token: str, message_id: str) -> dict[str, Any] | None:
    resp = await client.get(
        f"{GMAIL_API_URL}/users/me/messages/{message_id}",
        headers=_headers(token),
        params={"format": "metadata", "metadataHeaders": ["From", "Subject"]}
    )
    if not resp.is_success:
        return None
        
    m = resp.json()
    headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
    labels = m.get("labelIds", [])
    
    sender = headers.get("From", "")
    if "<" in sender:
        sender = sender.split("<")[0].strip().strip('"') or sender
        
    ts = datetime.fromtimestamp(int(m.get("internalDate", "0")) / 1000, timezone.utc)
    
    return {
        "id": m["id"],
        "sender": sender or "(unknown)",
        "subject": headers.get("Subject", "(no subject)"),
        "snippet": m.get("snippet", ""),
        "unread": "UNREAD" in labels,
        "important": "IMPORTANT" in labels,
        "received_at": ts.isoformat()
    }

async def fetch_calendar_events(token: str) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    time_min = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    time_max = (now + timedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{GCAL_API_URL}/calendars/primary/events",
            headers=_headers(token),
            params={
                "timeMin": time_min,
                "timeMax": time_max,
                "singleEvents": "true",
                "orderBy": "startTime",
                "maxResults": 50,
            },
        )
        if resp.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "token_invalid"},
            )
        resp.raise_for_status()

        events = []
        for item in resp.json().get("items", []):
            start_raw = item.get("start", {})
            end_raw = item.get("end", {})
            start_str = start_raw.get("dateTime") or start_raw.get("date")
            end_str = end_raw.get("dateTime") or end_raw.get("date")
            if not start_str or not end_str:
                continue

            meet_link = None
            for ep in item.get("conferenceData", {}).get("entryPoints", []):
                if ep.get("entryPointType") == "video":
                    meet_link = ep.get("uri")
                    break

            events.append({
                "id": item["id"],
                "title": item.get("summary", "(No title)"),
                "start": start_str,
                "end": end_str,
                "location": item.get("location"),
                "attendees": len(item.get("attendees", [])),
                "meet_link": meet_link,
            })
        return events


async def fetch_messages(token: str) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            f"{GMAIL_API_URL}/users/me/messages",
            headers=_headers(token),
            params={"maxResults": 10, "labelIds": "INBOX"}
        )
        if resp.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "token_invalid"}
            )
        resp.raise_for_status()
        
        message_refs = resp.json().get("messages", [])
        if not message_refs:
            return []
            
        tasks = [
            _fetch_message_metadata(client, token, ref["id"])
            for ref in message_refs
        ]
        
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
