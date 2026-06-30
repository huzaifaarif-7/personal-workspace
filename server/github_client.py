"""Async GitHub API client for the workspace dashboard.

This module contains ONLY raw GitHub API calls — no FastAPI, no DB, no routing.
Route handlers in github_routes.py call these functions and handle HTTP responses.

All functions accept a plaintext token (already decrypted by the caller).
Never log or expose the token string.

Error model
-----------
Two custom exceptions signal conditions the route layer needs to handle
specially instead of letting them bubble up as unhandled 500s:

    TokenRevokedError   — GitHub returned 401 (token expired / revoked)
    RateLimitedError    — GitHub returned 403 with x-ratelimit-remaining: 0

All other non-2xx responses raise httpx.HTTPStatusError (the caller decides
whether to re-raise as 502 or swallow).

Concurrency
-----------
fetch_summary() runs four independent GitHub calls in a single asyncio.gather()
so round-trip latency is bounded by the slowest call, not their sum.
"""
import asyncio
import logging
from datetime import datetime, timezone

import httpx

log = logging.getLogger("workspace.github")

GH_API = "https://api.github.com"
GH_TOKEN_URL = "https://github.com/login/oauth/access_token"

# Pinned API version — keeps behaviour stable across GitHub API updates.
_GH_API_VERSION = "2022-11-28"


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class TokenRevokedError(Exception):
    """Raised when GitHub returns HTTP 401 — the stored token is no longer valid."""


class RateLimitedError(Exception):
    """Raised when GitHub returns HTTP 403 with x-ratelimit-remaining == 0.

    Attributes:
        reset_at: ISO-8601 UTC string for when the rate limit window resets,
                  parsed from the x-ratelimit-reset epoch header.
    """
    def __init__(self, reset_at: str) -> None:
        self.reset_at = reset_at
        super().__init__(f"GitHub rate limit exceeded; resets at {reset_at}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _headers(token: str) -> dict:
    """Standard GitHub API request headers.

    Uses Bearer auth (preferred over token scheme), the JSON+GitHub accept
    header, and the pinned API version.  Never call this with a raw logged value.
    """
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": _GH_API_VERSION,
    }


def _check_response(resp: httpx.Response, token: str) -> None:
    """Raise a domain error for known GitHub error conditions.

    Must be called after every GitHub API response before reading .json().

    Args:
        resp:  The httpx Response object.
        token: Passed only so we can detect misuse — never logged or included
               in exception messages.

    Raises:
        TokenRevokedError: On HTTP 401.
        RateLimitedError:  On HTTP 403 with x-ratelimit-remaining header == "0".
        httpx.HTTPStatusError: On any other non-2xx status.
    """
    if resp.status_code == 401:
        # Log the exact GitHub response body so operators can see the reason
        # (e.g. "Bad credentials", "requires authentication") without any token exposure.
        try:
            body = resp.json()
        except Exception:
            body = resp.text[:200]
        log.warning(
            "GitHub API returned 401 — response body: %s  URL: %s",
            body,
            str(resp.url),
        )
        raise TokenRevokedError("GitHub token is no longer valid")

    if resp.status_code == 403:
        remaining = resp.headers.get("x-ratelimit-remaining", "1")
        if remaining == "0":
            reset_epoch = resp.headers.get("x-ratelimit-reset", "0")
            try:
                reset_dt = datetime.fromtimestamp(int(reset_epoch), tz=timezone.utc)
                reset_at = reset_dt.isoformat()
            except (ValueError, OSError):
                reset_at = "unknown"
            log.warning("GitHub rate limit exceeded; resets at %s", reset_at)
            raise RateLimitedError(reset_at)

    resp.raise_for_status()


# ---------------------------------------------------------------------------
# OAuth token exchange
# ---------------------------------------------------------------------------

async def exchange_code(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> str:
    """Exchange a GitHub OAuth authorisation code for an access token.

    Makes a POST to GitHub's token endpoint and returns the raw access_token
    string.  Raises ValueError if GitHub's response does not contain a token
    (e.g. the code was already used or expired).

    Args:
        code:          The `code` query param from the OAuth callback.
        client_id:     GITHUB_CLIENT_ID from settings.
        client_secret: GITHUB_CLIENT_SECRET from settings.
        redirect_uri:  Must exactly match the URI registered on the OAuth App.

    Returns:
        The plaintext GitHub access token.  Encrypt before storing.
    """
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            GH_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        resp.raise_for_status()

    payload = resp.json()
    token = payload.get("access_token")
    if not token:
        error = payload.get("error_description") or payload.get("error") or "unknown"
        raise ValueError(f"GitHub token exchange failed: {error}")
    return token


# ---------------------------------------------------------------------------
# Single-resource fetches (each runs inside a shared AsyncClient)
# ---------------------------------------------------------------------------

async def get_username(client: httpx.AsyncClient, token: str) -> str:
    """Return the authenticated user's GitHub login name.

    Args:
        client: Shared async HTTP client (caller owns lifecycle).
        token:  Plaintext GitHub access token.

    Returns:
        The GitHub username string (e.g. "octocat").
    """
    resp = await client.get(f"{GH_API}/user", headers=_headers(token))
    _check_response(resp, token)
    return resp.json()["login"]


async def _fetch_notifications(client: httpx.AsyncClient, token: str) -> list[dict]:
    """Fetch the 10 most recent unread GitHub notifications.

    GitHub's /notifications endpoint returns only unread items by default
    (all=false).  We cap at 10 on our side after parsing.

    Returns list of dicts: {id, repo, title, reason, unread, updated_at, url}
    """
    resp = await client.get(
        f"{GH_API}/notifications",
        headers=_headers(token),
        params={"all": "false", "per_page": 10},
    )
    _check_response(resp, token)

    out = []
    for n in resp.json()[:10]:
        subject = n.get("subject", {})
        out.append({
            "id": str(n.get("id", "")),
            "repo": n.get("repository", {}).get("full_name", ""),
            "title": subject.get("title", ""),
            "reason": n.get("reason", ""),
            "unread": n.get("unread", True),
            "updated_at": n.get("updated_at", ""),
            # subject.url is the API URL; latest_comment_url is also available
            "url": subject.get("url", ""),
        })
    return out


async def _fetch_pull_requests(client: httpx.AsyncClient, token: str) -> list[dict]:
    """Fetch open PRs where the user's review is requested.

    Uses the search API with q=is:pr+review-requested:@me+state:open.

    Returns list of dicts: {id, repo, title, url, updated_at}
    """
    resp = await client.get(
        f"{GH_API}/search/issues",
        headers=_headers(token),
        params={"q": "is:pr review-requested:@me state:open", "per_page": 10},
    )
    _check_response(resp, token)

    out = []
    for item in resp.json().get("items", [])[:10]:
        # Extract "owner/repo" from the repository_url field
        repo_url = item.get("repository_url", "")
        repo = "/".join(repo_url.rstrip("/").split("/")[-2:]) if repo_url else ""
        out.append({
            "id": str(item.get("number", item.get("id", ""))),
            "repo": repo,
            "title": item.get("title", ""),
            "url": item.get("html_url", ""),
            "updated_at": item.get("updated_at", ""),
        })
    return out


async def _fetch_assigned_issues(client: httpx.AsyncClient, token: str) -> list[dict]:
    """Fetch open issues assigned to the authenticated user.

    Uses the search API with q=is:issue+assignee:@me+state:open.

    Returns list of dicts: {id, repo, title, url, updated_at}
    """
    resp = await client.get(
        f"{GH_API}/search/issues",
        headers=_headers(token),
        params={"q": "is:issue assignee:@me state:open", "per_page": 10},
    )
    _check_response(resp, token)

    out = []
    for item in resp.json().get("items", [])[:10]:
        repo_url = item.get("repository_url", "")
        repo = "/".join(repo_url.rstrip("/").split("/")[-2:]) if repo_url else ""
        out.append({
            "id": str(item.get("number", item.get("id", ""))),
            "repo": repo,
            "title": item.get("title", ""),
            "url": item.get("html_url", ""),
            "updated_at": item.get("updated_at", ""),
        })
    return out


def _summarise_event(event: dict) -> str:
    """Build a short human-readable summary string for a GitHub event.

    Handles the most common event types; falls back to a generic label for
    anything not explicitly listed.
    """
    kind = event.get("type", "")
    repo = event.get("repo", {}).get("name", "")
    actor = event.get("actor", {}).get("login", "")
    payload = event.get("payload", {})

    if kind == "PushEvent":
        n = payload.get("size", len(payload.get("commits", [])))
        return f"Pushed {n} commit{'s' if n != 1 else ''} to {repo}"
    if kind == "PullRequestEvent":
        action = payload.get("action", "updated")
        pr_title = payload.get("pull_request", {}).get("title", "a PR")
        return f"{action.capitalize()} PR \"{pr_title}\" in {repo}"
    if kind == "IssuesEvent":
        action = payload.get("action", "updated")
        title = payload.get("issue", {}).get("title", "an issue")
        return f"{action.capitalize()} issue \"{title}\" in {repo}"
    if kind == "IssueCommentEvent":
        title = payload.get("issue", {}).get("title", "an issue")
        return f"Commented on \"{title}\" in {repo}"
    if kind == "CreateEvent":
        ref_type = payload.get("ref_type", "branch")
        ref = payload.get("ref") or repo
        return f"Created {ref_type} \"{ref}\" in {repo}"
    if kind == "DeleteEvent":
        ref_type = payload.get("ref_type", "branch")
        ref = payload.get("ref") or ""
        return f"Deleted {ref_type} \"{ref}\" from {repo}"
    if kind == "ForkEvent":
        return f"Forked {repo}"
    if kind == "WatchEvent":
        return f"Starred {repo}"
    if kind == "ReleaseEvent":
        tag = payload.get("release", {}).get("tag_name", "")
        return f"Released {tag} in {repo}"
    if kind == "PullRequestReviewEvent":
        state = payload.get("review", {}).get("state", "reviewed")
        pr_title = payload.get("pull_request", {}).get("title", "a PR")
        return f"{state.capitalize()} PR \"{pr_title}\" in {repo}"
    # Generic fallback
    return f"{kind.replace('Event', '')} in {repo}"


async def _fetch_recent_activity(
    client: httpx.AsyncClient,
    token: str,
    username: str,
) -> list[dict]:
    """Fetch the 10 most recent public events for the authenticated user.

    Returns list of dicts: {type, repo, summary, created_at}
    """
    resp = await client.get(
        f"{GH_API}/users/{username}/events",
        headers=_headers(token),
        params={"per_page": 30},   # fetch 30, cap to 10 meaningful ones
    )
    _check_response(resp, token)

    out = []
    for event in resp.json():
        if len(out) >= 10:
            break
        out.append({
            "type": event.get("type", ""),
            "repo": event.get("repo", {}).get("name", ""),
            "summary": _summarise_event(event),
            "created_at": event.get("created_at", ""),
        })
    return out


# ---------------------------------------------------------------------------
# Combined summary (concurrent)
# ---------------------------------------------------------------------------

async def fetch_summary(token: str, username: str) -> dict:
    """Fetch all four dashboard sections concurrently and return them combined.

    Runs notifications, pull_requests, assigned_issues, and recent_activity in
    a single asyncio.gather() over a shared AsyncClient — total latency is
    bounded by the slowest call, not the sum of all four.

    TokenRevokedError and RateLimitedError propagate up to the route handler,
    which maps them to HTTP 401 and HTTP 429 respectively.

    Args:
        token:    Plaintext GitHub access token (caller decrypts from DB).
        username: The stored GitHub username (avoids an extra /user API call).

    Returns:
        {
            "notifications":   [...],
            "pull_requests":   [...],
            "assigned_issues": [...],
            "recent_activity": [...],
        }
    """
    async with httpx.AsyncClient(timeout=20) as client:
        notifications, pull_requests, assigned_issues, recent_activity = (
            await asyncio.gather(
                _fetch_notifications(client, token),
                _fetch_pull_requests(client, token),
                _fetch_assigned_issues(client, token),
                _fetch_recent_activity(client, token, username),
            )
        )

    return {
        "notifications": notifications,
        "pull_requests": pull_requests,
        "assigned_issues": assigned_issues,
        "recent_activity": recent_activity,
    }
