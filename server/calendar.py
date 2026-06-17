"""Google Calendar endpoints (live with fallback)."""
from fastapi import APIRouter
from .. import schemas
from ..services import data

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/events", response_model=list[schemas.CalendarEvent])
def events(): return data.calendar_events()

@router.get("/today", response_model=list[schemas.CalendarEvent])
def today(): return data.today_events()

@router.post("/events", response_model=schemas.CalendarEvent, status_code=201)
def create_event(body: schemas.CreateEventRequest): return data.create_event(body)
