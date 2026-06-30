"""GitHub integration — pulls your recent activity feed using an OAuth token."""
import httpx

from . import schemas
from ._util import parse_iso

API = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def activity(token: str) -> list[schemas.GithubActivity]:
    with httpx.Client(timeout=20) as c:
        me = c.get(f"{API}/user", headers=_headers(token))
        me.raise_for_status()
        username = me.json()["login"]

        r = c.get(f"{API}/users/{username}/received_events",
                  headers=_headers(token), params={"per_page": 30})
        r.raise_for_status()

    out: list[schemas.GithubActivity] = []
    for e in r.json():
        kind = e.get("type")
        repo = e.get("repo", {}).get("name", "")
        actor = e.get("actor", {}).get("display_login") or e.get("actor", {}).get("login", "")
        ts = parse_iso(e.get("created_at"))
        p = e.get("payload", {})

        if kind == "PushEvent":
            commits = p.get("commits") or []
            n = p.get("size", len(commits))
            msg = commits[-1]["message"] if commits else "pushed commits"
            out.append(schemas.GithubActivity(id=str(e["id"]), actor=actor,
                       action=f"pushed {n} commits", repo=repo, message=msg,
                       commits=n, timestamp=ts))
        elif kind == "PullRequestEvent":
            pr = p.get("pull_request", {})
            out.append(schemas.GithubActivity(id=str(e["id"]), actor=actor,
                       action=f"{p.get('action', 'updated')} a pull request",
                       repo=repo, message=pr.get("title", ""), commits=0, timestamp=ts))
        elif kind == "CreateEvent":
            out.append(schemas.GithubActivity(id=str(e["id"]), actor=actor,
                       action=f"created {p.get('ref_type', '')}", repo=repo,
                       message=p.get("ref") or "", commits=0, timestamp=ts))
        if len(out) >= 12:
            break
    return out
