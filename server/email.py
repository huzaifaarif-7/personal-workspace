"""Email (Gmail) endpoints (live with fallback)."""
from fastapi import APIRouter
from . import schemas
from . import data

router = APIRouter(prefix="/email", tags=["email"])

@router.get("/messages", response_model=list[schemas.EmailMessage])
def messages(): return data.emails()

@router.get("/important", response_model=list[schemas.EmailMessage])
def important(): return [e for e in data.emails() if e.important]
