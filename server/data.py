"""Orchestration layer.

Each function returns LIVE data when the integration is connected, and falls
back to demo data (mock_data) on any error or when not connected — so the
dashboard always renders something and never crashes. Clients are imported
lazily so a missing optional library degrades to demo mode instead of a boot error.

GitHub and Gmail use per-user DB connections (GitHubConnection / EmailConnection).
When those providers are not connected for a user, the dashboard returns empty
lists rather than demo notifications.
"""
import logging

from sqlalchemy.orm import Session

from . import schemas
from .config import get_settings
from . import mock_data, store
from .crypto import decrypt_token
from .models import EmailConnection, GitHubConnection, SlackConnection, User
from ._util import ago, parse_iso

log = logging.getLogger("workspace")
settings = get_settings()


# ---------- connection status ----------
def status() -> dict[str, bool]:
    """Legacy global status (env tokens + in-memory store). Prefer status_for_user."""
    return {
        "slack": bool(settings.slack_user_token),
        "gcal": store.has("google"),
        "calendly": bool(settings.calendly_token),
        "github": store.has("github"),
        "email": store.has("google"),
    }


def status_for_user(db: Session, user_id: int) -> dict[str, bool]:
    gh = db.query(GitHubConnection).filter(GitHubConnection.user_id == user_id).first()
    em = db.query(EmailConnection).filter(EmailConnection.user_id == user_id).first()
    sl = db.query(SlackConnection).filter(SlackConnection.user_id == user_id).first()
    return {
        "slack": sl is not None or bool(settings.slack_user_token),
        "gcal": store.has("google"),
        "calendly": bool(settings.calendly_token),
        "github": gh is not None,
        "email": em is not None,
    }


def _try(provider: str, fn, fallback):
    """Run a live fetch; on any failure log and return the demo fallback."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        log.warning("live fetch for %s failed (%s) — using demo data", provider, e)
        return fallback()


# ---------- per integration ----------
def slack_messages_for_user(db: Session, user_id: int) -> list[schemas.SlackMessage]:
    conn = db.query(SlackConnection).filter(SlackConnection.user_id == user_id).first()
    token = None
    if conn:
        token = decrypt_token(conn.access_token_encrypted)
    elif settings.slack_user_token:
        token = settings.slack_user_token
        
    if not token:
        return mock_data.slack_messages()
    
    def live():
        from . import slack
        return slack.messages(token)
        
    msgs = _try("slack", live, mock_data.slack_messages)
    return msgs or mock_data.slack_messages()


def github_activity() -> list[schemas.GithubActivity]:
    tok = store.get("github")
    if not tok:
        return mock_data.github_activity()
    def live():
        from . import github
        return github.activity(tok["access_token"])
    items = _try("github", live, mock_data.github_activity)
    return items or mock_data.github_activity()


def github_activity_for_user(db: Session, user_id: int) -> list[schemas.GithubActivity]:
    conn = db.query(GitHubConnection).filter(GitHubConnection.user_id == user_id).first()
    if not conn:
        return []
    try:
        from . import github
        token = decrypt_token(conn.access_token_encrypted)
        return github.activity(token)
    except Exception as e:  # noqa: BLE001
        log.warning("live github fetch for user_id=%s failed (%s)", user_id, e)
        return []


def calendly_overview() -> schemas.CalendlyOverview:
    if not settings.calendly_token:
        return mock_data.calendly_overview()
    def live():
        from . import calendly
        return calendly.overview(settings.calendly_token)
    return _try("calendly", live, mock_data.calendly_overview)


def calendar_events() -> list[schemas.CalendarEvent]:
    tok = store.get("google")
    if not tok:
        return mock_data.calendar_events()
    def live():
        from . import google
        return google.calendar_events(tok)
    return _try("gcal", live, mock_data.calendar_events)


def today_events() -> list[schemas.CalendarEvent]:
    today = __import__("datetime").datetime.now().date()
    return [e for e in calendar_events() if e.start.date() == today]


def create_event(req: schemas.CreateEventRequest) -> schemas.CalendarEvent:
    tok = store.get("google")
    if tok:
        try:
            from . import google
            return google.create_event(tok, req)
        except Exception as e:  # noqa: BLE001
            log.warning("live create_event failed (%s) — writing to demo store", e)
    return mock_data.create_event(req)


def emails() -> list[schemas.EmailMessage]:
    tok = store.get("google")
    if not tok:
        return mock_data.emails()
    def live():
        from . import google
        return google.emails(tok)
    items = _try("email", live, mock_data.emails)
    return items or mock_data.emails()


async def emails_for_user(db: Session, user_id: int) -> list[schemas.EmailMessage]:
    from .google_client import fetch_messages, get_valid_google_token

    conn = db.query(EmailConnection).filter(EmailConnection.user_id == user_id).first()
    if not conn:
        return []
    try:
        token = await get_valid_google_token(db, conn)
        raw = await fetch_messages(token)
    except Exception as e:  # noqa: BLE001
        log.warning("live email fetch for user_id=%s failed (%s)", user_id, e)
        return []

    out: list[schemas.EmailMessage] = []
    for m in raw:
        out.append(schemas.EmailMessage(
            id=m["id"],
            sender=m["sender"],
            subject=m["subject"],
            preview=m["snippet"],
            timestamp=parse_iso(m["received_at"]),
            unread=m["unread"],
            important=m.get("important", False),
        ))
    return out


# ---------- aggregate payload for the frontend ----------
INTEGRATION_META = {
    "slack": ("Slack", "Mentions, DMs & channels"),
    "gcal": ("Google Calendar", "Events & Google Meet"),
    "calendly": ("Calendly", "Bookings & availability"),
    "github": ("GitHub", "Commits & repo activity"),
    "email": ("Gmail", "Inbox & important mail"),
}


async def dashboard_payload(user: User, db: Session) -> dict:
    st = status_for_user(db, user.id)
    slack = slack_messages_for_user(db, user.id) if st["slack"] else []
    cal = calendar_events()
    cly = calendly_overview()
    gh = github_activity_for_user(db, user.id) if st["github"] else []
    mail = await emails_for_user(db, user.id) if st["email"] else []

    return {
        "user": {"name": user.full_name},
        "live": any(st.values()),
        "integrations": [
            {"id": k, "name": INTEGRATION_META[k][0],
             "description": INTEGRATION_META[k][1], "connected": st[k]}
            for k in INTEGRATION_META
        ],
        "slack": {
            "mentions": [
                {"id": m.id, "from": m.sender, "channel": m.channel,
                 "text": m.text, "time": ago(m.timestamp), "unread": m.unread}
                for m in slack if m.kind == "mention"
            ],
            "dms": [
                {"id": m.id, "from": m.sender, "text": m.text,
                 "time": ago(m.timestamp), "unread": m.unread}
                for m in slack if m.kind == "dm"
            ],
        },
        "calendar": [
            {"id": e.id, "title": e.title, "start": e.start.isoformat(),
             "end": e.end.isoformat(), "priority": e.priority,
             "location": e.location, "attendees": e.attendees,
             "meet": bool(e.meet_link)}
            for e in cal
        ],
        "calendly": {
            "link": cly.booking_link, "availability": cly.availability,
            "booked": [
                {"id": b.id, "name": b.name, "with": b.invitee,
                 "time": b.when, "type": b.duration}
                for b in cly.bookings
            ],
        },
        "github": [
            {"id": g.id, "actor": g.actor, "action": g.action, "repo": g.repo,
             "message": g.message, "commits": g.commits, "time": ago(g.timestamp),
             "pr": "pull request" in g.action}
            for g in gh
        ],
        "email": [
            {"id": e.id, "from": e.sender, "subject": e.subject,
             "preview": e.preview, "time": ago(e.timestamp),
             "unread": e.unread, "important": e.important}
            for e in mail
        ],
    }
