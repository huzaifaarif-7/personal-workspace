"""Orchestration layer.

Each function returns LIVE data when the integration is connected, and falls
back to demo data (mock_data) on any error or when not connected — so the
dashboard always renders something and never crashes. Clients are imported
lazily so a missing optional library degrades to demo mode instead of a boot error.
"""
import logging

from . import schemas
from .config import get_settings
from . import mock_data, store
from ._util import ago

log = logging.getLogger("workspace")
settings = get_settings()


# ---------- connection status ----------
def status() -> dict[str, bool]:
    return {
        "slack": bool(settings.slack_user_token),
        "gcal": store.has("google"),
        "calendly": bool(settings.calendly_token),
        "github": store.has("github"),
        "email": store.has("google"),
    }


def _try(provider: str, fn, fallback):
    """Run a live fetch; on any failure log and return the demo fallback."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        log.warning("live fetch for %s failed (%s) — using demo data", provider, e)
        return fallback()


# ---------- per integration ----------
def slack_messages() -> list[schemas.SlackMessage]:
    if not settings.slack_user_token:
        return mock_data.slack_messages()
    def live():
        from . import slack
        return slack.messages(settings.slack_user_token)
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


# ---------- aggregate payload for the frontend ----------
INTEGRATION_META = {
    "slack": ("Slack", "Mentions, DMs & channels"),
    "gcal": ("Google Calendar", "Events & Google Meet"),
    "calendly": ("Calendly", "Bookings & availability"),
    "github": ("GitHub", "Commits & repo activity"),
    "email": ("Gmail", "Inbox & important mail"),
}


def dashboard_payload(user_name: str) -> dict:
    st = status()
    slack = slack_messages()
    cal = calendar_events()
    cly = calendly_overview()
    gh = github_activity()
    mail = emails()

    return {
        "user": {"name": user_name},
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
