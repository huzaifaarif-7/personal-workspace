"""Single aggregate endpoint the frontend calls on load."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import data
from .database import get_db
from .deps import get_current_user
from .models import User

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard")
async def dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await data.dashboard_payload(user, db)

@router.get("/integrations/status")
def integrations_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return data.status_for_user(db, user.id)
