"""Pydantic models shared across routers (request + response shapes)."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field

Priority = Literal["high", "medium", "low"]


# ---------- Auth ----------
class SignupRequest(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    password: str = Field(..., max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class UserPublic(BaseModel):
    id: str
    name: str = Field(..., max_length=100)
    email: EmailStr


# ---------- Integrations ----------
class Integration(BaseModel):
    id: str
    name: str = Field(..., max_length=100)
    connected: bool
    description: str = Field(..., max_length=500)
    last_sync: Optional[datetime] = None


class ConnectRequest(BaseModel):
    # In production this carries the OAuth code/redirect; mocked here.
    code: Optional[str] = None


# ---------- Slack ----------
class SlackMessage(BaseModel):
    id: str
    sender: str = Field(..., max_length=100)
    channel: Optional[str] = Field(None, max_length=100)
    text: str = Field(..., max_length=2000)
    timestamp: datetime
    unread: bool = False
    kind: Literal["mention", "dm"]


# ---------- Calendar ----------
class CalendarEvent(BaseModel):
    id: str
    title: str = Field(..., max_length=200)
    start: datetime
    end: datetime
    priority: Priority = "medium"
    location: Optional[str] = Field(None, max_length=200)
    attendees: int = 0
    meet_link: Optional[str] = Field(None, max_length=500)


class CreateEventRequest(BaseModel):
    title: str = Field(..., max_length=200)
    start: datetime
    end: datetime
    priority: Priority = "medium"
    add_meet: bool = True


# ---------- Calendly ----------
class CalendlyBooking(BaseModel):
    id: str
    name: str = Field(..., max_length=100)
    invitee: str = Field(..., max_length=100)
    when: str = Field(..., max_length=100)
    duration: str = Field(..., max_length=50)


class CalendlyOverview(BaseModel):
    booking_link: str
    availability: str
    bookings: list[CalendlyBooking]


# ---------- GitHub ----------
class GithubActivity(BaseModel):
    id: str
    actor: str = Field(..., max_length=100)
    action: str = Field(..., max_length=100)
    repo: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    commits: int
    timestamp: datetime


# ---------- Email ----------
class EmailMessage(BaseModel):
    id: str
    sender: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=300)
    preview: str = Field(..., max_length=500)
    timestamp: datetime
    unread: bool
    important: bool


# ---------- Assistant ----------
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=4000)


class AssistantQuery(BaseModel):
    message: str = Field(..., max_length=1000)
    history: list[ChatMessage] = []


class AssistantReply(BaseModel):
    reply: str = Field(..., max_length=4000)
    source: Literal["anthropic", "local"]


TokenResponse.model_rebuild()
