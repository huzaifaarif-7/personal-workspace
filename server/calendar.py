"""Google Calendar endpoints (live with fallback)."""
from fastapi import APIRouter
from . import schemas
from . import data
from fastapi import Depends
from .deps import get_current_user
from .models import User

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/events", response_model=list[schemas.CalendarEvent])
def events(user: User = Depends(get_current_user)): return data.calendar_events()

@router.get("/today", response_model=list[schemas.CalendarEvent])
def today(user: User = Depends(get_current_user)): return data.today_events()

@router.post("/events", response_model=schemas.CalendarEvent, status_code=201)
def create_event(body: schemas.CreateEventRequest, user: User = Depends(get_current_user)): return data.create_event(body)
