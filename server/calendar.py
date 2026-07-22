"""Google Calendar endpoints — live per-user data via stored OAuth token."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import data, schemas
from .database import get_db
from .deps import get_current_user
from .models import User

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/events", response_model=list[schemas.CalendarEvent])
async def events(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await data.calendar_events_for_user(db, user.id)


@router.get("/today", response_model=list[schemas.CalendarEvent])
async def today(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    all_events = await data.calendar_events_for_user(db, user.id)
    today_date = datetime.now(timezone.utc).date()
    return [e for e in all_events if e.start.date() == today_date]


@router.post("/events", response_model=schemas.CalendarEvent, status_code=201)
def create_event(body: schemas.CreateEventRequest, user: User = Depends(get_current_user)):
    return data.create_event(body)
