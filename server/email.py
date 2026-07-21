"""Email (Gmail) endpoints (live with fallback)."""
from fastapi import APIRouter
from . import schemas
from . import data
from fastapi import Depends
from .deps import get_current_user
from .models import User

router = APIRouter(prefix="/email", tags=["email"])

@router.get("/messages", response_model=list[schemas.EmailMessage])
def messages(user: User = Depends(get_current_user)): return data.emails()

@router.get("/important", response_model=list[schemas.EmailMessage])
def important(user: User = Depends(get_current_user)): return [e for e in data.emails() if e.important]
