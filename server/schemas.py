"""Pydantic models shared across routers (request + response shapes)."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr

Priority = Literal["high", "medium", "low"]


# ---------- Auth ----------
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr


# ---------- Integrations ----------
class Integration(BaseModel):
    id: str
    name: str
    connected: bool
    description: str
    last_sync: Optional[datetime] = None


class ConnectRequest(BaseModel):
    # In production this carries the OAuth code/redirect; mocked here.
    code: Optional[str] = None


# ---------- Slack ----------
class SlackMessage(BaseModel):
    id: str
    sender: str
    channel: Optional[str] = None
    text: str
    timestamp: datetime
    unread: bool = False
    kind: Literal["mention", "dm"]


# ---------- Calendar ----------
class CalendarEvent(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime
    priority: Priority = "medium"
    location: Optional[str] = None
    attendees: int = 0
    meet_link: Optional[str] = None


class CreateEventRequest(BaseModel):
    title: str
    start: datetime
    end: datetime
    priority: Priority = "medium"
    add_meet: bool = True


# ---------- Calendly ----------
class CalendlyBooking(BaseModel):
    id: str
    name: str
    invitee: str
    when: str
    duration: str


class CalendlyOverview(BaseModel):
    booking_link: str
    availability: str
    bookings: list[CalendlyBooking]


# ---------- GitHub ----------
class GithubActivity(BaseModel):
    id: str
    actor: str
    action: str
    repo: str
    message: str
    commits: int
    timestamp: datetime


# ---------- Email ----------
class EmailMessage(BaseModel):
    id: str
    sender: str
    subject: str
    preview: str
    timestamp: datetime
    unread: bool
    important: bool


# ---------- Assistant ----------
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AssistantQuery(BaseModel):
    message: str
    history: list[ChatMessage] = []


class AssistantReply(BaseModel):
    reply: str
    source: Literal["anthropic", "local"]


TokenResponse.model_rebuild()
