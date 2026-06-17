"""Slack integration — your mentions (search) and DM previews (user token).

Note: search.messages requires a user token and search availability can depend
on your Slack plan. If search is unavailable, mentions return empty and the
orchestrator falls back to demo data for that section.
"""
from datetime import datetime, timezone

import httpx

from ... import schemas

BASE = "https://slack.com/api"


def _get(c: httpx.Client, method: str, token: str, **params) -> dict:
    r = c.get(f"{BASE}/{method}", headers={"Authorization": f"Bearer {token}"},
              params=params)
    r.raise_for_status()
    return r.json()


def _ts(ts: str) -> datetime:
    try:
        return datetime.fromtimestamp(float(ts), timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def messages(token: str) -> list[schemas.SlackMessage]:
    out: list[schemas.SlackMessage] = []
    with httpx.Client(timeout=20) as c:
        who = _get(c, "auth.test", token)
        uid = who.get("user_id")

        # ----- mentions via search -----
        try:
            srch = _get(c, "search.messages", token, query=f"<@{uid}>",
                        count=8, sort="timestamp")
            if srch.get("ok"):
                for m in srch.get("messages", {}).get("matches", []):
                    out.append(schemas.SlackMessage(
                        id=m.get("iid", m.get("ts", "")),
                        sender=m.get("username", "someone"),
                        channel="#" + m.get("channel", {}).get("name", "channel"),
                        text=m.get("text", ""), timestamp=_ts(m.get("ts", "0")),
                        unread=True, kind="mention"))
        except Exception:
            pass

        # ----- DM previews -----
        try:
            ims = _get(c, "conversations.list", token, types="im", limit=10)
            users: dict[str, str] = {}
            for ch in ims.get("channels", [])[:6]:
                hist = _get(c, "conversations.history", token,
                            channel=ch["id"], limit=1)
                msgs = hist.get("messages", [])
                if not msgs:
                    continue
                msg = msgs[0]
                peer = ch.get("user", "")
                if peer and peer not in users:
                    info = _get(c, "users.info", token, user=peer)
                    users[peer] = (info.get("user", {}).get("real_name")
                                   or info.get("user", {}).get("name", "Direct message"))
                out.append(schemas.SlackMessage(
                    id=msg.get("ts", ""), sender=users.get(peer, "Direct message"),
                    channel=None, text=msg.get("text", ""),
                    timestamp=_ts(msg.get("ts", "0")),
                    unread=bool(ch.get("is_unread")), kind="dm"))
        except Exception:
            pass
    return out
