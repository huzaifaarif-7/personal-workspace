"""In-memory data layer that simulates the external integrations.

In production each function below would call the real provider SDK/API
(Slack Web API, Google Calendar API, GitHub REST API, Gmail API, Calendly API)
using the user's stored OAuth tokens. The router layer stays identical —
only these functions change.
"""
from datetime import datetime, timedelta
from uuid import uuid4

from . import schemas

_now = datetime.now


def _at(hour: int, minute: int, day_offset: int = 0) -> datetime:
    d = _now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    return d + timedelta(days=day_offset)


# Demo users (replace with a real DB). Password for both is "password".
USERS: dict[str, dict] = {}

# In-memory calendar so create-event has a real side effect.
_events: list[schemas.CalendarEvent] = [
    schemas.CalendarEvent(id="c1", title="Daily Standup", start=_at(9, 30), end=_at(9, 45),
                          priority="low", location="Google Meet", attendees=6,
                          meet_link="https://meet.google.com/abc-defg-hij"),
    schemas.CalendarEvent(id="c2", title="Design Review", start=_now() + timedelta(minutes=25),
                          end=_now() + timedelta(minutes=70), priority="high",
                          location="Google Meet", attendees=5,
                          meet_link="https://meet.google.com/dsg-revw-001"),
    schemas.CalendarEvent(id="c3", title="1:1 with Ayesha", start=_at(15, 0), end=_at(15, 30),
                          priority="medium", location="Google Meet", attendees=2,
                          meet_link="https://meet.google.com/one-on-one"),
    schemas.CalendarEvent(id="c4", title="Product Sync", start=_at(17, 30), end=_at(18, 0),
                          priority="high", location="Conference Room B", attendees=8),
    schemas.CalendarEvent(id="c5", title="Roadmap Planning", start=_at(11, 0, 1), end=_at(12, 0, 1),
                          priority="high", location="Google Meet", attendees=6,
                          meet_link="https://meet.google.com/roadmap"),
]

INTEGRATIONS: list[schemas.Integration] = [
    schemas.Integration(id="slack", name="Slack", connected=True,
                        description="Mentions, DMs & channels", last_sync=_now()),
    schemas.Integration(id="gcal", name="Google Calendar", connected=True,
                        description="Events & Google Meet", last_sync=_now()),
    schemas.Integration(id="calendly", name="Calendly", connected=True,
                        description="Bookings & availability", last_sync=_now()),
    schemas.Integration(id="github", name="GitHub", connected=True,
                        description="Commits & repo activity", last_sync=_now()),
    schemas.Integration(id="email", name="Gmail", connected=True,
                        description="Inbox & important mail", last_sync=_now()),
]


def list_integrations() -> list[schemas.Integration]:
    return INTEGRATIONS


def set_connected(integration_id: str, connected: bool) -> schemas.Integration:
    for it in INTEGRATIONS:
        if it.id == integration_id:
            it.connected = connected
            it.last_sync = _now() if connected else None
            return it
    raise KeyError(integration_id)


def slack_messages() -> list[schemas.SlackMessage]:
    return [
        schemas.SlackMessage(id="s1", sender="Ahmed Raza", channel="#product", kind="mention",
                             text="@Huzaifa can you review the new onboarding flow before the 3pm sync?",
                             timestamp=_now() - timedelta(minutes=8), unread=True),
        schemas.SlackMessage(id="s2", sender="Sara Khan", channel="#engineering", kind="mention",
                             text="@Huzaifa the API rate-limit fix is deployed to staging 🎉",
                             timestamp=_now() - timedelta(minutes=41), unread=True),
        schemas.SlackMessage(id="s3", sender="Bilal", channel="#design", kind="mention",
                             text="@Huzaifa loved the new dashboard mocks — shipping today?",
                             timestamp=_now() - timedelta(hours=2), unread=False),
        schemas.SlackMessage(id="s4", sender="Ayesha Malik", kind="dm",
                             text="Are we still on for the 1:1 later today?",
                             timestamp=_now() - timedelta(minutes=15), unread=True),
        schemas.SlackMessage(id="s5", sender="Usman", kind="dm",
                             text="Sent over the contract draft, take a look when free.",
                             timestamp=_now() - timedelta(hours=1), unread=False),
    ]


def calendar_events() -> list[schemas.CalendarEvent]:
    return sorted(_events, key=lambda e: e.start)


def today_events() -> list[schemas.CalendarEvent]:
    today = _now().date()
    return [e for e in calendar_events() if e.start.date() == today]


def create_event(req: schemas.CreateEventRequest) -> schemas.CalendarEvent:
    ev = schemas.CalendarEvent(
        id=str(uuid4())[:8], title=req.title, start=req.start, end=req.end,
        priority=req.priority, location="Google Meet" if req.add_meet else "In person",
        attendees=0,
        meet_link=f"https://meet.google.com/new-{uuid4().hex[:6]}" if req.add_meet else None,
    )
    _events.append(ev)
    return ev


def calendly_overview() -> schemas.CalendlyOverview:
    return schemas.CalendlyOverview(
        booking_link="calendly.com/huzaifa/30min",
        availability="Available",
        bookings=[
            schemas.CalendlyBooking(id="b1", name="Intro Call", invitee="Daniel Wright",
                                    when="Tomorrow · 1:00 PM", duration="30 min"),
            schemas.CalendlyBooking(id="b2", name="Product Walkthrough", invitee="Priya Nair",
                                    when="Thu · 4:30 PM", duration="45 min"),
            schemas.CalendlyBooking(id="b3", name="Discovery Call", invitee="Tom Becker",
                                    when="Fri · 11:00 AM", duration="30 min"),
        ],
    )


def github_activity() -> list[schemas.GithubActivity]:
    return [
        schemas.GithubActivity(id="g1", actor="Ali Hassan", action="pushed 5 commits",
                               repo="backend-api", commits=5,
                               message="feat: add rate limiting + retry logic to integration layer",
                               timestamp=_now() - timedelta(minutes=10)),
        schemas.GithubActivity(id="g2", actor="Sara Khan", action="opened a pull request",
                               repo="web-dashboard", commits=0,
                               message="Dark theme polish & responsive sidebar",
                               timestamp=_now() - timedelta(minutes=38)),
        schemas.GithubActivity(id="g3", actor="Huzaifa", action="pushed 2 commits",
                               repo="ai-assistant", commits=2,
                               message="chore: refine assistant system prompt",
                               timestamp=_now() - timedelta(hours=1)),
        schemas.GithubActivity(id="g4", actor="Bilal", action="merged a pull request",
                               repo="web-dashboard", commits=0,
                               message="Add Calendly integration cards",
                               timestamp=_now() - timedelta(hours=3)),
    ]


def emails() -> list[schemas.EmailMessage]:
    return [
        schemas.EmailMessage(id="e1", sender="Stripe", subject="Your invoice for May is ready",
                             preview="Your subscription invoice of $49.00 has been paid successfully.",
                             timestamp=_now() - timedelta(minutes=12), unread=True, important=True),
        schemas.EmailMessage(id="e2", sender="Daniel Wright", subject="Re: Partnership proposal",
                             preview="Thanks for the deck — the team is excited. Can we lock a call this week?",
                             timestamp=_now() - timedelta(minutes=47), unread=True, important=True),
        schemas.EmailMessage(id="e3", sender="GitHub", subject="[web-dashboard] 2 new pull requests",
                             preview="Sara Khan and Bilal opened pull requests in your repository.",
                             timestamp=_now() - timedelta(hours=1), unread=True, important=False),
        schemas.EmailMessage(id="e4", sender="Notion", subject="Weekly digest: 4 pages updated",
                             preview="Your team updated the Product Roadmap and 3 other pages.",
                             timestamp=_now() - timedelta(hours=4), unread=False, important=False),
    ]
