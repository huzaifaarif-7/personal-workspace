"""SQLAlchemy ORM models for the workspace dashboard.

All models inherit from `Base` (defined in server.database). The schema is
pre-applied in Supabase — this file reflects it but never recreates it.

Schema is intentionally multi-user-ready:
  - User is the root entity; every integration record belongs to one User.
  - Each connection table has a unique FK to User so that one user can have
    at most one connected account per provider (unique=True).
  - Access/refresh tokens are stored encrypted — see server.crypto for the
    encrypt_token / decrypt_token helpers.  Never store plaintext tokens.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


def _utcnow() -> datetime:
    """Return a timezone-aware UTC datetime (used as column defaults)."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    """A workspace user.

    Identity is established via a session cookie containing the user ID.
    Users sign up with their email and a hashed password.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Back-references
    github_connection = relationship(
        "GitHubConnection", back_populates="user", uselist=False
    )
    email_connection = relationship(
        "EmailConnection", back_populates="user", uselist=False
    )
    slack_connection = relationship(
        "SlackConnection", back_populates="user", uselist=False
    )
    calendar_connection = relationship(
        "CalendarConnection", back_populates="user", uselist=False
    )
    preferences = relationship(
        "UserPreferences", back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} full_name={self.full_name!r}>"


# ---------------------------------------------------------------------------
# UserPreferences
# ---------------------------------------------------------------------------

class UserPreferences(Base):
    """Per-user UI preferences (theme, font) persisted across sessions."""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    theme = Column(String, nullable=False, default="dark")
    font = Column(String, nullable=False, default="Inter")
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferences user_id={self.user_id} theme={self.theme!r} font={self.font!r}>"


# ---------------------------------------------------------------------------
# GitHubConnection
# ---------------------------------------------------------------------------

class GitHubConnection(Base):
    """Stores a user's GitHub OAuth token (encrypted) and metadata."""
    __tablename__ = "github_connections"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_github_connections_user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    github_username = Column(String(255), nullable=False)
    access_token_encrypted = Column(Text, nullable=False)
    scopes = Column(String(512), nullable=False, default="")
    connected_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    user = relationship("User", back_populates="github_connection")

    def __repr__(self) -> str:
        return f"<GitHubConnection id={self.id} user_id={self.user_id} github_username={self.github_username!r}>"


# ---------------------------------------------------------------------------
# EmailConnection
# ---------------------------------------------------------------------------

class EmailConnection(Base):
    """Stores a user's Gmail OAuth tokens (encrypted) and metadata."""
    __tablename__ = "email_connections"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_email_connections_user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    email_address = Column(String(320), nullable=False)
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    connected_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    user = relationship("User", back_populates="email_connection")

    def __repr__(self) -> str:
        return f"<EmailConnection id={self.id} user_id={self.user_id} email_address={self.email_address!r}>"


# ---------------------------------------------------------------------------
# SlackConnection
# ---------------------------------------------------------------------------

class SlackConnection(Base):
    """Stores a user's Slack OAuth tokens (encrypted) and metadata."""
    __tablename__ = "slack_connections"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_slack_connections_user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    slack_user_id = Column(String(255), nullable=False)
    access_token_encrypted = Column(Text, nullable=False)
    connected_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    user = relationship("User", back_populates="slack_connection")

    def __repr__(self) -> str:
        return f"<SlackConnection id={self.id} user_id={self.user_id} slack_user_id={self.slack_user_id!r}>"


# ---------------------------------------------------------------------------
# CalendarConnection
# ---------------------------------------------------------------------------

class CalendarConnection(Base):
    """Stores a user's Google Calendar OAuth tokens (encrypted) and metadata."""
    __tablename__ = "calendar_connections"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_calendar_connections_user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    connected_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    user = relationship("User", back_populates="calendar_connection")

    def __repr__(self) -> str:
        return f"<CalendarConnection id={self.id} user_id={self.user_id}>"
