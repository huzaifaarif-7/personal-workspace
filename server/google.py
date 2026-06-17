"""Google integration — Calendar (read + create) and Gmail (read)."""
import base64
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from ... import schemas
from ...config import get_settings
from ...services import store
from ._util import parse_iso

settings = get_settings()

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid", "email",
]


def _creds(token: dict) -> Credentials:
    creds = Credentials(
        token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=token.get("scopes", SCOPES),
    )
    # refresh transparently and persist the new access token
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token["access_token"] = creds.token
        store.save("google", token)
    return creds


def _svc(token: dict, name: str, ver: str):
    return build(name, ver, credentials=_creds(token), cache_discovery=False)


def _priority(ev: dict) -> str:
    # heuristic: more attendees / longer => higher priority (no native field)
    n = len(ev.get("attendees", []))
    return "high" if n >= 5 else "medium" if n >= 2 else "low"


def calendar_events(token: dict) -> list[schemas.CalendarEvent]:
    svc = _svc(token, "calendar", "v3")
    now = datetime.now(timezone.utc).isoformat()
    res = svc.events().list(calendarId="primary", timeMin=now, maxResults=20,
                            singleEvents=True, orderBy="startTime").execute()
    out = []
    for it in res.get("items", []):
        start = it["start"].get("dateTime") or it["start"].get("date")
        end = it["end"].get("dateTime") or it["end"].get("date")
        out.append(schemas.CalendarEvent(
            id=it["id"], title=it.get("summary", "(no title)"),
            start=parse_iso(start), end=parse_iso(end),
            priority=_priority(it),
            location=("Google Meet" if it.get("hangoutLink") else it.get("location") or "—"),
            attendees=len(it.get("attendees", [])),
            meet_link=it.get("hangoutLink")))
    return out


def today_events(token: dict) -> list[schemas.CalendarEvent]:
    today = datetime.now().date()
    return [e for e in calendar_events(token) if e.start.date() == today]


def create_event(token: dict, req: schemas.CreateEventRequest) -> schemas.CalendarEvent:
    svc = _svc(token, "calendar", "v3")
    body = {
        "summary": req.title,
        "start": {"dateTime": req.start.isoformat()},
        "end": {"dateTime": req.end.isoformat()},
    }
    kwargs = {}
    if req.add_meet:
        body["conferenceData"] = {"createRequest": {
            "requestId": f"hw-{int(datetime.now().timestamp())}",
            "conferenceSolutionKey": {"type": "hangoutsMeet"}}}
        kwargs["conferenceDataVersion"] = 1
    it = svc.events().insert(calendarId="primary", body=body, **kwargs).execute()
    return schemas.CalendarEvent(
        id=it["id"], title=it.get("summary", req.title),
        start=parse_iso(it["start"].get("dateTime")),
        end=parse_iso(it["end"].get("dateTime")),
        priority=req.priority, location="Google Meet" if req.add_meet else "—",
        attendees=0, meet_link=it.get("hangoutLink"))


def emails(token: dict) -> list[schemas.EmailMessage]:
    svc = _svc(token, "gmail", "v1")
    listing = svc.users().messages().list(userId="me", maxResults=8,
                                           labelIds=["INBOX"]).execute()
    out = []
    for ref in listing.get("messages", []):
        m = svc.users().messages().get(userId="me", id=ref["id"],
                                       format="metadata",
                                       metadataHeaders=["From", "Subject"]).execute()
        headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
        labels = m.get("labelIds", [])
        sender = headers.get("From", "")
        if "<" in sender:
            sender = sender.split("<")[0].strip().strip('"') or sender
        ts = datetime.fromtimestamp(int(m.get("internalDate", "0")) / 1000, timezone.utc)
        out.append(schemas.EmailMessage(
            id=ref["id"], sender=sender or "(unknown)",
            subject=headers.get("Subject", "(no subject)"),
            preview=m.get("snippet", ""), timestamp=ts,
            unread=("UNREAD" in labels), important=("IMPORTANT" in labels)))
    return out
