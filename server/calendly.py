"""Calendly integration — booking link and upcoming scheduled calls (PAT)."""
import httpx

from . import schemas
from ._util import parse_iso

BASE = "https://api.calendly.com"


def overview(token: str) -> schemas.CalendlyOverview:
    h = {"Authorization": f"Bearer {token}"}
    with httpx.Client(timeout=20) as c:
        me = c.get(f"{BASE}/users/me", headers=h)
        me.raise_for_status()
        user = me.json()["resource"]
        uri, link = user["uri"], user["scheduling_url"]

        ev = c.get(f"{BASE}/scheduled_events", headers=h, params={
            "user": uri, "status": "active", "sort": "start_time:asc", "count": 8})
        ev.raise_for_status()

        bookings = []
        for e in ev.json().get("collection", [])[:6]:
            start = parse_iso(e.get("start_time"))
            invitee = ""
            try:
                inv = c.get(f"{e['uri']}/invitees", headers=h, params={"count": 1})
                coll = inv.json().get("collection", [])
                if coll:
                    invitee = coll[0].get("name", "")
            except Exception:
                pass
            bookings.append(schemas.CalendlyBooking(
                id=e["uri"].rstrip("/").split("/")[-1],
                name=e.get("name", "Meeting"),
                invitee=invitee or "—",
                when=start.strftime("%a %d %b · %I:%M %p"),
                duration=e.get("location", {}).get("type", "")))
    return schemas.CalendlyOverview(
        booking_link=link.replace("https://", "").replace("http://", ""),
        availability="Available", bookings=bookings)
