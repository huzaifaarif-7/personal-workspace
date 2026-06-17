"""Token store for OAuth providers (GitHub, Google).

Uses Upstash Redis over its REST API when configured (survives serverless cold
starts on Vercel), and falls back to an in-memory dict otherwise — so it works
unchanged on a long-running host like Render/Railway. Any Redis error degrades
gracefully to memory instead of breaking the request.
"""
import json
import logging
from threading import Lock

import httpx

from ..config import get_settings

settings = get_settings()
log = logging.getLogger("workspace")

_lock = Lock()
_mem: dict[str, dict] = {}
_USE_REDIS = bool(settings.upstash_redis_rest_url and settings.upstash_redis_rest_token)


def _cmd(args: list):
    r = httpx.post(settings.upstash_redis_rest_url,
                   headers={"Authorization": f"Bearer {settings.upstash_redis_rest_token}"},
                   json=args, timeout=10)
    r.raise_for_status()
    return r.json().get("result")


def _key(provider: str) -> str:
    return f"hw:token:{provider}"


def save(provider: str, token: dict) -> None:
    if _USE_REDIS:
        try:
            _cmd(["SET", _key(provider), json.dumps(token)])
            return
        except Exception as e:  # noqa: BLE001
            log.warning("redis save failed (%s) — falling back to memory", e)
    with _lock:
        _mem[provider] = token


def get(provider: str) -> dict | None:
    if _USE_REDIS:
        try:
            v = _cmd(["GET", _key(provider)])
            return json.loads(v) if v else None
        except Exception as e:  # noqa: BLE001
            log.warning("redis get failed (%s) — falling back to memory", e)
    return _mem.get(provider)


def has(provider: str) -> bool:
    return get(provider) is not None


def clear(provider: str) -> None:
    if _USE_REDIS:
        try:
            _cmd(["DEL", _key(provider)])
            return
        except Exception:  # noqa: BLE001
            pass
    with _lock:
        _mem.pop(provider, None)
