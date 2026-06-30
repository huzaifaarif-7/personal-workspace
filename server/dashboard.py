"""Single aggregate endpoint the frontend calls on load."""
from fastapi import APIRouter, Depends
from . import data
from .deps import get_current_user
from .models import User

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user)): 
    return data.dashboard_payload(user.full_name)

@router.get("/integrations/status")
def integrations_status(user: User = Depends(get_current_user)): 
    return data.status()
