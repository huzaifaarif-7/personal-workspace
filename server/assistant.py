"""AI assistant with intent routing and RAG-style context filtering.

Flow: extract intent → route to one data source → filter by person/date/limit
      → build focused context → send to LLM (or format locally if no key).
"""
import re
from datetime import datetime, date, timedelta

import httpx

from .config import get_settings
from . import data

settings = get_settings()

# ─── Compiled regexes ────────────────────────────────────────────────────────

_ACTION_CREATE = re.compile(
    r"\b(create|schedule|set up|add|book)\b.{0,40}(meeting|event|call|appointment)",
    re.I,
)
_SRC_SLACK  = re.compile(r"\bslack\b|\bmentions?\b|\bmentioned\b|\btagged\b|\bdm\b|\bchannels?\b", re.I)
_SRC_GITHUB = re.compile(r"\bgithub\b|\bcommit\w*|\bpush\w*|\brepos?\b|\bpull.?requests?\b|\bpr\b", re.I)
_SRC_EMAIL  = re.compile(r"\bemails?\b|\bmail\b|\binbox\b|\bgmail\b", re.I)
_SRC_CAL    = re.compile(r"\bcalendar\b|\bmeetings?\b|\bevents?\b|\bschedule\b", re.I)
_LATEST     = re.compile(r"\b(latest|most recent|newest|just|last|recently)\b", re.I)
_PERSON_PRE = re.compile(
    r"(?:from|by|about|with|did|has)\s+([A-Za-z][a-zA-Z]+)",
    re.I,
)
_PERSON_SFX = re.compile(
    r"\b([A-Za-z][a-zA-Z]+)\s+(?:message|mentioned|dm|email|mail|commit|pushed)\b",
    re.I,
)
_STOP_WORDS = {
    "me", "i", "my", "you", "we", "us", "it", "a", "the",
    "do", "did", "get", "got", "any", "all", "some",
    "who", "what", "when", "where", "which", "how",
    "text", "message", "send", "sent", "say", "said",
    "last", "latest", "recent", "yesterday", "today", "tomorrow",
}


def _extract_intent(message: str) -> dict:
    intent: dict = {
        "action":      "read",
        "source":      None,
        "person":      None,
        "date_filter": None,
        "result_type": "list",
        "limit":       5,
    }

    # Action intents bypass RAG entirely
    if _ACTION_CREATE.search(message):
        intent["action"] = "create_calendar_event"
        return intent

    # Source — most specific first
    if _SRC_SLACK.search(message):
        intent["source"] = "slack"
    elif _SRC_GITHUB.search(message):
        intent["source"] = "github"
    elif _SRC_EMAIL.search(message):
        intent["source"] = "email"
    elif _SRC_CAL.search(message):
        intent["source"] = "calendar"

    # Result type / limit
    if _LATEST.search(message):
        intent["result_type"] = "latest"
        intent["limit"] = 1
    elif re.search(r"\b(summary|overview|happening|snapshot|brief)\b", message, re.I):
        intent["result_type"] = "summary"

    # Date filter
    if re.search(r"\byesterday\b", message, re.I):
        intent["date_filter"] = "yesterday"
    elif re.search(r"\btomorrow\b", message, re.I):
        intent["date_filter"] = "tomorrow"
    elif re.search(r"\btoday\b", message, re.I) and intent["source"] != "calendar":
        intent["date_filter"] = "today"
    elif re.search(r"\bthis week\b|\bpast week\b|\blast 7 days\b", message, re.I):
        intent["date_filter"] = "week"

    # Person — prefer preposition match, fall back to suffix match
    m = _PERSON_PRE.search(message) or _PERSON_SFX.search(message)
    if m:
        candidate = m.group(1).strip().lower()
        if candidate not in _STOP_WORDS:
            # Keep original casing for display
            raw = m.group(1).strip()
            intent["person"] = raw

    return intent


# ─── Date filter ─────────────────────────────────────────────────────────────

def _apply_date_filter(items: list, date_filter: str | None, attr: str) -> list:
    if not date_filter:
        return items
    today = date.today()
    if date_filter == "today":
        tgt = today
        return [i for i in items if getattr(i, attr, None) and getattr(i, attr).date() == tgt]
    if date_filter == "yesterday":
        tgt = today - timedelta(days=1)
        return [i for i in items if getattr(i, attr, None) and getattr(i, attr).date() == tgt]
    if date_filter == "tomorrow":
        tgt = today + timedelta(days=1)
        return [i for i in items if getattr(i, attr, None) and getattr(i, attr).date() == tgt]
    if date_filter == "week":
        cutoff = today - timedelta(days=7)
        return [i for i in items if getattr(i, attr, None) and getattr(i, attr).date() >= cutoff]
    return items


def _fmt(dt: datetime) -> str:
    return dt.strftime("%a %d %b, %I:%M %p")


def _clean_channel(ch: str | None) -> str:
    """Return a human-readable channel label; replace raw Slack IDs with 'DM'."""
    if not ch:
        return "DM"
    inner = ch.lstrip("#")
    # Slack user/channel IDs: start with U, C, D, G, W followed by alphanumerics
    if re.match(r"^[UCDGBW][A-Z0-9]{6,}$", inner):
        return "DM"
    return ch


# ─── Per-source data retrieval ────────────────────────────────────────────────

def _fetch_slack(db, user_id: int, intent: dict, raw: str) -> list[dict]:
    msgs = data.slack_messages_for_user(db, user_id)

    if re.search(r"\bmentioned?\b|\btagged\b", raw, re.I):
        msgs = [m for m in msgs if m.kind == "mention"]
    elif re.search(r"\bdm\b|\bdirect\b", raw, re.I):
        msgs = [m for m in msgs if m.kind == "dm"]

    if intent.get("person"):
        p = intent["person"].lower()
        msgs = [m for m in msgs if p in m.sender.lower()]

    msgs.sort(key=lambda m: m.timestamp, reverse=True)
    return [
        {"source": "Slack", "from": m.sender,
         "channel": _clean_channel(m.channel),
         "date": m.timestamp.strftime("%a %d %b"),
         "time": m.timestamp.strftime("%I:%M %p"),
         "text": m.text, "type": m.kind}
        for m in msgs[:intent["limit"]]
    ]


async def _fetch_email(db, user_id: int, intent: dict, raw: str) -> list[dict]:
    mails = await data.emails_for_user(db, user_id)

    if re.search(r"\b(important|urgent)\b", raw, re.I):
        mails = [m for m in mails if m.important]
    if re.search(r"\b(unread|new)\b", raw, re.I):
        mails = [m for m in mails if m.unread]
    if intent.get("person"):
        p = intent["person"].lower()
        mails = [m for m in mails if p in m.sender.lower()]

    mails = _apply_date_filter(mails, intent.get("date_filter"), "timestamp")
    mails.sort(key=lambda m: m.timestamp, reverse=True)
    return [
        {"source": "Gmail", "from": m.sender, "subject": m.subject,
         "preview": m.preview, "time": _fmt(m.timestamp),
         "unread": m.unread, "important": m.important}
        for m in mails[:intent["limit"]]
    ]


async def _fetch_calendar(db, user_id: int, intent: dict, raw: str) -> list[dict]:
    events = await data.calendar_events_for_user(db, user_id)

    date_f = intent.get("date_filter") or "today"
    if re.search(r"\btomorrow\b", raw, re.I):
        date_f = "tomorrow"
    elif re.search(r"\bweek\b|\bupcoming\b", raw, re.I):
        date_f = "week"

    events = _apply_date_filter(events, date_f, "start")
    events.sort(key=lambda e: e.start)
    return [
        {"source": "Calendar", "title": e.title,
         "start": _fmt(e.start), "end": e.end.strftime("%I:%M %p"),
         "priority": e.priority, "location": e.location or ""}
        for e in events
    ]


def _fetch_github(db, user_id: int, intent: dict) -> list[dict]:
    items = data.github_activity_for_user(db, user_id)

    if intent.get("person"):
        p = intent["person"].lower()
        items = [g for g in items if p in g.actor.lower()]

    items = _apply_date_filter(items, intent.get("date_filter"), "timestamp")
    items.sort(key=lambda g: g.timestamp, reverse=True)
    return [
        {"source": "GitHub", "actor": g.actor, "action": g.action,
         "repo": g.repo, "message": g.message, "time": _fmt(g.timestamp)}
        for g in items[:intent["limit"]]
    ]


async def _fetch_summary(db, user_id: int) -> list[dict]:
    slack = data.slack_messages_for_user(db, user_id)
    mentions = sorted(
        [m for m in slack if m.kind == "mention"],
        key=lambda m: m.timestamp, reverse=True,
    )[:2]

    mails = await data.emails_for_user(db, user_id)
    important = [m for m in mails if m.important][:3]
    unread_ct = sum(1 for m in mails if m.unread)

    events = await data.calendar_events_for_user(db, user_id)
    today_evts = sorted(
        [e for e in events if e.start.date() == date.today()],
        key=lambda e: e.start,
    )

    gh = sorted(
        data.github_activity_for_user(db, user_id),
        key=lambda g: g.timestamp, reverse=True,
    )[:2]

    items: list[dict] = []
    for m in mentions:
        items.append({"source": "Slack", "from": m.sender,
                      "text": m.text, "time": _fmt(m.timestamp)})
    for e in today_evts:
        items.append({"source": "Calendar", "title": e.title, "start": _fmt(e.start)})
    for m in important:
        items.append({"source": "Gmail", "from": m.sender,
                      "subject": m.subject, "important": True})
    items.append({"source": "Gmail", "unread_count": unread_ct})
    for g in gh:
        items.append({"source": "GitHub", "actor": g.actor,
                      "action": g.action, "repo": g.repo})
    return items


# ─── Context rendering ────────────────────────────────────────────────────────

def _items_to_text(items: list[dict]) -> str:
    if not items:
        return "No relevant data found."
    lines = []
    for it in items:
        src = it.get("source", "")
        if src == "Slack":
            lines.append(
                f"[Slack]\n"
                f"  From: {it['from']}\n"
                f"  Channel: {it.get('channel', 'DM')}\n"
                f"  Date: {it.get('date', '')}  Time: {it.get('time', '')}\n"
                f"  Message: {it.get('text', '').strip()}"
            )
        elif src == "GitHub":
            lines.append(
                f"[GitHub] {it['actor']} {it['action']} → {it['repo']} | {it['time']}"
                + (f"\n  {it['message']}" if it.get("message") else "")
            )
        elif src == "Gmail":
            if "unread_count" in it:
                lines.append(f"[Gmail] Total unread: {it['unread_count']}")
            else:
                lines.append(
                    f"[Gmail] From: {it['from']} | Subject: {it.get('subject', '')} "
                    f"| Important: {it.get('important', False)} | Time: {it.get('time', '')}"
                    + (f"\n  Preview: {it['preview']}" if it.get("preview") else "")
                )
        elif src == "Calendar":
            if "end" in it:
                lines.append(
                    f"[Calendar] {it['title']} | {it['start']} — {it['end']} "
                    f"| Priority: {it.get('priority', '')}"
                )
            else:
                lines.append(f"[Calendar] {it.get('title', '')} at {it.get('start', '')}")
    return "\n\n".join(lines)


def _local_format(items: list[dict], intent: dict) -> str:
    src    = intent.get("source")
    person = intent.get("person")
    rtype  = intent.get("result_type")
    date_f = intent.get("date_filter")

    if not items:
        if src == "slack":
            return (f"No Slack messages from {person} found."
                    if person else "No new Slack mentions right now.")
        if src == "github":
            period = f" for {date_f}" if date_f else ""
            return f"No GitHub activity found{period}."
        if src == "email":
            return "No emails found matching your criteria."
        if src == "calendar":
            return "No calendar events found for that period."
        return "No relevant workspace data found."

    if src == "slack":
        header = (
            "Latest Slack mention:" if rtype == "latest"
            else f"Messages from {person}:" if person
            else "Recent Slack messages:"
        )
        blocks = []
        for i in items:
            blocks.append(
                f"From: {i['from']}\n"
                f"Channel: {i.get('channel', 'DM')}\n"
                f"Date: {i.get('date', '')}\n"
                f"Time: {i.get('time', '')}\n"
                f"Message:\n{i.get('text', '').strip()}"
            )
        sep = "\n\n" + "─" * 20 + "\n\n"
        return header + "\n\n" + sep.join(blocks)

    if src == "github":
        lines = [f"• {i['actor']} {i['action']} → {i['repo']} ({i['time']})" for i in items]
        return "GitHub activity:\n" + "\n".join(lines)

    if src == "email":
        lines = [f"• From {i['from']} — {i['subject']}" for i in items]
        return f"{len(items)} email(s) found:\n" + "\n".join(lines)

    if src == "calendar":
        lines = [f"• {i['start']} — {i['title']}" for i in items]
        return "Meetings:\n" + "\n".join(lines)

    # Summary
    greeting = "morning" if datetime.now().hour < 12 else "afternoon"
    lines = []
    for it in items:
        s = it.get("source", "")
        if s == "Slack":
            lines.append(f"• Slack: {it['from']} mentioned you — \"{it.get('text', '')[:60]}\"")
        elif s == "Calendar":
            lines.append(f"• Meeting: {it.get('title')} at {it.get('start')}")
        elif s == "Gmail" and "unread_count" in it:
            lines.append(f"• {it['unread_count']} unread emails")
        elif s == "Gmail":
            lines.append(f"• Important email from {it['from']}: {it.get('subject')}")
        elif s == "GitHub":
            lines.append(f"• GitHub: {it['actor']} {it['action']} → {it['repo']}")
    return f"Good {greeting}! Here's your workspace snapshot:\n" + "\n".join(lines)


# ─── Main entry point ─────────────────────────────────────────────────────────

async def answer(
    user_name: str,
    message: str,
    history: list[dict],
    db=None,
    user_id: int | None = None,
) -> tuple[str, str]:
    intent = _extract_intent(message)

    if intent["action"] == "create_calendar_event":
        return (
            "I can help plan that, but I can't write to your calendar directly yet. "
            "Head to the Calendar tab and tap the + button — you can set the time, "
            "priority, and attendees there.",
            "local",
        )

    # Fetch only the relevant data source
    if db is not None and user_id is not None:
        src   = intent.get("source")
        rtype = intent.get("result_type")
        if rtype == "summary" or src is None:
            items = await _fetch_summary(db, user_id)
        elif src == "slack":
            items = _fetch_slack(db, user_id, intent, message)
        elif src == "email":
            items = await _fetch_email(db, user_id, intent, message)
        elif src == "calendar":
            items = await _fetch_calendar(db, user_id, intent, message)
        else:  # github
            items = _fetch_github(db, user_id, intent)
    else:
        items = []

    if not settings.openrouter_api_key:
        return _local_format(items, intent), "local"

    context_text = _items_to_text(items)
    system = (
        f"You are \"{user_name}'s Assistant\", a concise, friendly productivity assistant.\n"
        f"Today is {datetime.now().strftime('%A, %d %B %Y, %I:%M %p')}.\n\n"
        f"Answer ONLY from the context provided below. If the context has no relevant data, "
        f"say so clearly and briefly. Do NOT reference data sources that aren't in the context. "
        f"Use bullet points for lists. Be direct.\n\n"
        f"Context:\n{context_text}"
    )

    try:
        r = httpx.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": settings.frontend_url,
                "X-Title": "Workspace",
            },
            json={
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": system},
                    *history,
                    {"role": "user", "content": message},
                ],
                "max_tokens": 600,
            },
            timeout=40,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        return text or _local_format(items, intent), "openrouter"
    except Exception:
        return _local_format(items, intent), "local"
