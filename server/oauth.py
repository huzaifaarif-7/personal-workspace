"""OAuth connect flows for GitHub and Google.

Visit /api/auth/github/login or /api/auth/google/login in a browser to connect.
After approval the provider redirects to the matching /callback, we store the
token, and send the user back to the frontend.
"""
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from ..config import get_settings
from ..services import store

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["oauth"])

GITHUB_SCOPES = "repo read:user"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid", "email",
]


def _frontend_redirect(provider: str, ok: bool) -> RedirectResponse:
    return RedirectResponse(f"{settings.frontend_url}/?connected={provider}&ok={int(ok)}")


# ---------------- GitHub ----------------
@router.get("/github/login")
def github_login():
    if not settings.github_client_id:
        raise HTTPException(500, "GITHUB_CLIENT_ID not configured")
    url = ("https://github.com/login/oauth/authorize"
           f"?client_id={settings.github_client_id}"
           f"&redirect_uri={settings.github_callback_url}"
           f"&scope={GITHUB_SCOPES.replace(' ', '%20')}")
    return RedirectResponse(url)


@router.get("/github/callback")
def github_callback(code: str | None = None):
    if not code:
        return _frontend_redirect("github", False)
    r = httpx.post("https://github.com/login/oauth/access_token",
                   headers={"Accept": "application/json"},
                   data={"client_id": settings.github_client_id,
                         "client_secret": settings.github_client_secret,
                         "code": code,
                         "redirect_uri": settings.github_callback_url}, timeout=20)
    token = r.json().get("access_token")
    if not token:
        return _frontend_redirect("github", False)
    store.save("github", {"access_token": token})
    return _frontend_redirect("github", True)


# ---------------- Google ----------------
def _google_flow(state: str | None = None):
    from google_auth_oauthlib.flow import Flow
    cfg = {"web": {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [settings.google_callback_url],
    }}
    flow = Flow.from_client_config(cfg, scopes=GOOGLE_SCOPES, state=state)
    flow.redirect_uri = settings.google_callback_url
    return flow


@router.get("/google/login")
def google_login():
    if not settings.google_client_id:
        raise HTTPException(500, "GOOGLE_CLIENT_ID not configured")
    flow = _google_flow()
    url, _ = flow.authorization_url(access_type="offline", prompt="consent",
                                    include_granted_scopes="true")
    return RedirectResponse(url)


@router.get("/google/callback")
def google_callback(request: Request):
    try:
        flow = _google_flow()
        flow.fetch_token(authorization_response=str(request.url))
        creds = flow.credentials
        store.save("google", {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "scopes": list(creds.scopes or GOOGLE_SCOPES),
        })
        return _frontend_redirect("google", True)
    except Exception:
        return _frontend_redirect("google", False)
