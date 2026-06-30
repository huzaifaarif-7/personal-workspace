from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .crypto import hash_password, verify_password
from .database import get_db
from .models import User

log = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="", tags=["user"])

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@auth_router.post("/signup")
def signup(req: SignupRequest, request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not req.full_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_input", "reason": "full_name_empty"}
        )
    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_input", "reason": "password_too_short"}
        )
        
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "email_taken"}
        )
        
    user = User(
        full_name=req.full_name.strip(),
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log them in automatically
    request.session["user_id"] = user.id
    
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
    }

@auth_router.post("/login")
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials"}
        )
        
    request.session["user_id"] = user.id
    
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
    }

@auth_router.post("/logout")
def logout(request: Request) -> dict[str, Any]:
    request.session.clear()
    return {"ok": True}

@user_router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    user_id = request.session.get("user_id")
    if not user_id:
        return {"authenticated": False}
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"authenticated": False}
        
    return {
        "authenticated": True,
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
    }
