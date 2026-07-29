from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import assistant
from .database import get_db
from .deps import get_current_user
from .models import User
from .schemas import AssistantQuery

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/query")
async def assistant_query(
    body: AssistantQuery,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    history = [{"role": m.role, "content": m.content} for m in body.history]
    reply, source = await assistant.answer(
        user_name=user.full_name,
        message=body.message,
        history=history,
        db=db,
        user_id=user.id,
    )
    return {"reply": reply, "source": source}
