# Huzaifa's Workspace — single Vercel project

Frontend (Vite + React) and backend (FastAPI) in **one project, one domain**.
Vercel serves the frontend and routes `/api/*` to the Python function — same
origin, no CORS.

```
.
├── api/index.py        Vercel Python entrypoint → exposes the FastAPI app
├── server/             FastAPI app (routers, OAuth, integration clients, assistant)
├── src/                React frontend (Workspace.jsx + main.jsx)
├── index.html, vite.config.js, package.json   Vite app
├── requirements.txt    Python deps (installed for the function)
├── vercel.json         function timeout + SPA rewrite
└── .env                local dev only (gitignored)
```

## Local development (two terminals)

```bash
# backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --reload          # http://localhost:8000/api/docs

# frontend
npm install
npm run dev                                 # http://localhost:5173
```
Locally the frontend talks to `http://localhost:8000/api` (the built-in default).

## Deploy to Vercel

1. Push this folder to a GitHub repo and import it as **one** Vercel project.
   Leave **Root Directory empty**. Vercel auto-detects Vite (frontend) and the
   Python function in `api/` — no framework preset needed.
2. Add the environment variables from `.env.production.example` in
   Project → Settings → Environment Variables. Use **new** values for any token
   that was shared during setup.
3. Create a free **Upstash Redis** DB and set `UPSTASH_REDIS_REST_URL` +
   `UPSTASH_REDIS_REST_TOKEN` — without this, GitHub/Google won't stay connected
   across serverless invocations. (Calendly/Slack use static tokens and are fine.)
4. Deploy. Check `https://personalworkspace.vercel.app/api/health`.

## Exact values for personalworkspace.vercel.app

Vercel env vars:
```
FRONTEND_URL=https://personalworkspace.vercel.app
GITHUB_CALLBACK_URL=https://personalworkspace.vercel.app/api/auth/github/callback
GOOGLE_CALLBACK_URL=https://personalworkspace.vercel.app/api/auth/google/callback
VITE_API_BASE=/api
```

OAuth dashboards (make sure these are EXACTLY what's registered):
- GitHub → Authorization callback URL:
  `https://personalworkspace.vercel.app/api/auth/github/callback`
- Google Cloud → Authorized redirect URI:
  `https://personalworkspace.vercel.app/api/auth/google/callback`
- Google Cloud → Authorized JavaScript origin (optional):
  `https://personalworkspace.vercel.app`

## Watch out for

- **Bundle size**: the Google client libraries are large; if the function build
  fails on Vercel's 500MB limit, host the backend separately on Render/Railway
  (the code runs there unchanged). Everything else stays the same.
- **Cold starts**: first request after idle is slow.
- **Connect GitHub/Google** after deploy via the Settings page (or open
  `/api/auth/github/login` and `/api/auth/google/login`). Calendly + Slack are
  already live from their tokens.
- Regenerate every token pasted in plain text during setup before going live.
