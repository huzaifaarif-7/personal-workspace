"""Single aggregate endpoint the frontend calls on load."""
from fastapi import APIRouter
from ..services import data

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard")
def dashboard(): return data.dashboard_payload()

@router.get("/integrations/status")
def integrations_status(): return data.status()
