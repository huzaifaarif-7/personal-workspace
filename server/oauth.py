"""OAuth connect flows for Google (Gmail + Calendar).

GitHub OAuth is handled by server.github_routes (includes CSRF state,
DB persistence via GitHubConnection model, and token encryption).

Visit /api/auth/google/login in a browser to connect Google.
After approval the provider redirects to /api/auth/google/callback, we store
the token via the legacy store module, and send the user back to the frontend.
"""
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from .config import get_settings
from . import store

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["oauth"])

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
    print("GitHub redirect URI:", settings.github_redirect_uri)
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
