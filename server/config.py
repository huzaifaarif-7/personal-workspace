"""Application configuration loaded from environment variables (.env)."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Huzaifa's Workspace API"
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:5173"   # where to send users after OAuth

    # Auth
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24

    # GitHub OAuth
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_callback_url: str = "http://localhost:8000/api/auth/github/callback"

    # Google OAuth (Calendar + Gmail)
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_callback_url: str = "http://localhost:8000/api/auth/google/callback"

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

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
