"""AI assistant logic — answers over your live workspace data via OpenRouter.

OpenRouter is OpenAI-compatible, so we POST to {base}/chat/completions. If no key
is set (or the call fails), a deterministic local summary is returned instead, so
the assistant always responds.
"""
import re
from datetime import datetime

import httpx

from .config import get_settings
from . import data

settings = get_settings()


def build_context(user_name: str) -> dict:
    events = data.calendar_events()
    nxt = next((e for e in events if e.start.replace(tzinfo=None) > datetime.now()), None)
    slack = data.slack_messages()
    mail = data.emails()
    gh = data.github_activity()
    today = data.today_events()
    return {
        "user": user_name,
        "now": datetime.now().strftime("%A %d %B, %I:%M %p"),
        "slack_mentions": [{"from": m.sender, "channel": m.channel, "text": m.text}
                           for m in slack if m.kind == "mention"],
        "today_meetings": [{"title": e.title, "time": e.start.strftime("%I:%M %p"),
                            "priority": e.priority} for e in today],
        "next_meeting": ({"title": nxt.title, "time": nxt.start.strftime("%I:%M %p")}
                         if nxt else None),
        "emails": {"unread": sum(1 for e in mail if e.unread),
                   "important": [{"from": e.sender, "subject": e.subject}
                                 for e in mail if e.important]},
        "github": [{"who": g.actor, "what": g.action, "repo": g.repo} for g in gh],
    }


def local_reply(message: str, ctx: dict) -> str:
    t = message.lower()
    name = ctx["user"]
    if re.search(r"(urgent|important).*(email|mail)|email.*(urgent|important)", t):
        imp = ctx["emails"]["important"]
        return f"You have {len(imp)} important email(s):\n" + \
               "\n".join(f"• {e['from']} — {e['subject']}" for e in imp)
    if re.search(r"commit|repo|github|push", t):
        return "Recent GitHub activity:\n" + \
               "\n".join(f"• {g['who']} {g['what']} to {g['repo']}" for g in ctx["github"][:3])
    if re.search(r"slack|mention|tagged", t):
        ms = ctx["slack_mentions"]
        if not ms:
            return "No new Slack mentions right now."
        return f"You were mentioned by {', '.join(m['from'] for m in ms)}."
    if re.search(r"email|mail|inbox", t):
        e = ctx["emails"]
        return f"You have {e['unread']} unread emails, {len(e['important'])} important."
    greeting = "morning" if datetime.now().hour < 12 else "afternoon"
    nxt = (f"\nYour next meeting is {ctx['next_meeting']['title']} at "
           f"{ctx['next_meeting']['time']}." if ctx["next_meeting"] else "")
    return (f"Good {greeting} {name} 👋\nHere's your snapshot:\n"
            f"• {len(ctx['slack_mentions'])} new Slack mentions\n"
            f"• {len(ctx['today_meetings'])} meetings today\n"
            f"• {ctx['emails']['unread']} new emails ({len(ctx['emails']['important'])} important)\n"
            + (f"• {ctx['github'][0]['who']} {ctx['github'][0]['what']} to "
               f"{ctx['github'][0]['repo']}" if ctx["github"] else "") + nxt)


def answer(user_name: str, message: str, history: list[dict]) -> tuple[str, str]:
    ctx = build_context(user_name)
    if not settings.openrouter_api_key:
        return local_reply(message, ctx), "local"

    system = (f"You are \"{user_name}'s Assistant\", a warm, friendly, professional "
              f"productivity assistant. Be concise, use • bullets for lists, occasionally "
              f"use the user's name and a light emoji. Answer ONLY from this workspace "
              f"data:\n{ctx}")
    try:
        r = httpx.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}",
                     "Content-Type": "application/json",
                     "HTTP-Referer": settings.frontend_url,
                     "X-Title": "Workspace"},
            json={"model": settings.llm_model,
                  "messages": [{"role": "system", "content": system}, *history,
                               {"role": "user", "content": message}],
                  "max_tokens": 800},
            timeout=40)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        return text or local_reply(message, ctx), "openrouter"
    except Exception:
        return local_reply(message, ctx), "local"
