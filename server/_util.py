"""Shared helpers for integration clients."""
from datetime import datetime, timezone


def parse_iso(s: str | None) -> datetime:
    if not s:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def ago(dt: datetime) -> str:
    """Human 'time ago' label: 8m, 2h, 3d."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    secs = (datetime.now(timezone.utc) - dt).total_seconds()
    if secs < 60:   return "now"
    if secs < 3600: return f"{int(secs // 60)}m"
    if secs < 86400: return f"{int(secs // 3600)}h"
    return f"{int(secs // 86400)}d"
