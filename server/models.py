"""SQLAlchemy ORM models for the workspace dashboard.

All models inherit from `Base` (defined in server.database) so that a single
`Base.metadata.create_all(engine)` call on startup creates every table.

Schema is intentionally multi-user-ready:
  - User is the root entity; every integration record belongs to one User.
  - GitHubConnection and EmailConnection each have a unique FK to User so that
    one user can have at most one connected account per provider (unique=True).
  - Access/refresh tokens are stored encrypted — see server.crypto for the
    encrypt_token / decrypt_token helpers.  Never store plaintext tokens.

To add a new provider later, create a new model that mirrors GitHubConnection:
  id, user_id (FK+unique), provider-specific fields, access_token_encrypted,
  connected_at.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

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

    # Back-references — allows user.github_connection and user.email_connection
    github_connection = relationship(
        "GitHubConnection", back_populates="user", uselist=False
    )
    email_connection = relationship(
        "EmailConnection", back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} full_name={self.full_name!r}>"


# ---------------------------------------------------------------------------
# GitHubConnection
# ---------------------------------------------------------------------------

class GitHubConnection(Base):
    """Stores a user's GitHub OAuth token (encrypted) and metadata.

    `access_token_encrypted` holds the output of crypto.encrypt_token().
    Call crypto.decrypt_token(row.access_token_encrypted) to get the live token.

    `scopes` is a space-separated string of granted OAuth scopes, e.g.
    "repo read:user".  Store it as-is from the GitHub token response.
    """
    __tablename__ = "github_connections"

    # Enforce that each user can have at most one GitHub connection at the
    # DB level (in addition to the unique=True on the FK column).
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_github_connections_user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,    # one GitHub account per user
        index=True,
    )
    github_username = Column(String(255), nullable=False)
    access_token_encrypted = Column(Text, nullable=False)   # never plaintext
    scopes = Column(String(512), nullable=False, default="")
    connected_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # ORM relationship back to the owner User
    user = relationship("User", back_populates="github_connection")

    def __repr__(self) -> str:
        return (
            f"<GitHubConnection id={self.id} "
            f"user_id={self.user_id} "
            f"github_username={self.github_username!r}>"
        )


# ---------------------------------------------------------------------------
# EmailConnection
# ---------------------------------------------------------------------------

class EmailConnection(Base):
    """Stores a user's Gmail OAuth tokens (encrypted) and metadata.

    Gmail uses both an access token (short-lived) and a refresh token
    (long-lived, nullable because some flows don't return one on re-auth).
    `token_expiry` is the UTC datetime when the access token expires.

    Refresh flow (to implement later):
        if datetime.now(utc) >= row.token_expiry:
            new_token = google_refresh(decrypt_token(row.refresh_token_encrypted))
            row.access_token_encrypted = encrypt_token(new_token.access_token)
            row.token_expiry = new_token.expiry
            db.commit()
    """
    __tablename__ = "email_connections"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_email_connections_user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,    # one Gmail account per user
        index=True,
    )
    email_address = Column(String(320), nullable=False)
    access_token_encrypted = Column(Text, nullable=False)       # never plaintext
    refresh_token_encrypted = Column(Text, nullable=True)       # nullable — not always returned
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    connected_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # ORM relationship back to the owner User
    user = relationship("User", back_populates="email_connection")

    def __repr__(self) -> str:
        return (
            f"<EmailConnection id={self.id} "
            f"user_id={self.user_id} "
            f"email_address={self.email_address!r}>"
        )
