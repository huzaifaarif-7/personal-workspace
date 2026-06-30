"""Application configuration loaded from environment variables (.env)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Workspace API"
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:5173"   # where to send users after OAuth

    # --- Session (Starlette SessionMiddleware) ---
    # SESSION_SECRET_KEY must be set in .env — no default is provided so that
    # startup fails loudly rather than silently using a weak/shared key.
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    session_secret_key: str

    # --- Token encryption (see server.crypto) ---
    # TOKEN_ENCRYPTION_KEY is also read directly by crypto.py at import time
    # (with a hard RuntimeError if missing).  Declaring it here too lets
    # pydantic-settings validate it and expose it via get_settings().
    token_encryption_key: str | None = None

    # Auth (legacy JWT fields — kept for backward compatibility)
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24

    # GitHub OAuth
    github_client_id: str | None = None
    github_client_secret: str | None = None
    # github_callback_url reads GITHUB_CALLBACK_URL (legacy field, kept for compat)
    github_callback_url: str = "http://localhost:8000/api/auth/github/callback"
    # github_redirect_uri reads GITHUB_REDIRECT_URI — used by the new OAuth routes
    github_redirect_uri: str = "http://localhost:8000/api/auth/github/callback"

    # Google OAuth (Calendar + Gmail)
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_callback_url: str = "http://localhost:8000/api/auth/google/callback"
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # Calendly + Slack (static personal tokens)
    calendly_token: str | None = None
    slack_user_token: str | None = None

    # Optional persistent token store (recommended on serverless / Vercel).
    # Upstash Redis REST — works over plain HTTPS, no redis client needed.
    upstash_redis_rest_url: str | None = None
    upstash_redis_rest_token: str | None = None

    # Extra allowed CORS origins (comma-separated), e.g. your Vercel frontend URL.
    extra_cors: str = ""

    # Assistant via OpenRouter (OpenAI-compatible)
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str | None = None
    llm_model: str = "google/gemma-4-31b-it:free"

    cors_origins: list[str] = [
        "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
