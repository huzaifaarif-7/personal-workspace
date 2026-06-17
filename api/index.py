"""Vercel Python entrypoint.

Vercel detects this file in /api, packages it as a serverless function, and
routes all /api/* requests to it. We add the repo root to sys.path so the
`server` FastAPI package imports cleanly regardless of the function's CWD.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main import app  # noqa: E402  (exposed for Vercel)
