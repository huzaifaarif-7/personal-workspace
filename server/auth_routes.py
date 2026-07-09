from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .crypto import hash_password, verify_password
from .database import get_db
from .models import User

log = logging.getLogger(__name__)

from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)


auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="", tags=["user"])

class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

@auth_router.post("/signup")
@limiter.limit("3/minute")
def signup(req: SignupRequest, request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    log.info("signup: received request for email=%s", req.email)

    if not req.full_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_input", "reason": "full_name_empty"}
        )
    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "password_too_short", "min_length": 8}
        )
    if len(req.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_input", "reason": "password_too_long"}
        )

    log.info("signup: querying DB for existing user")
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "email_taken"}
        )

    log.info("signup: hashing password (bcrypt — expect ~200-500ms)")
    password_hash = hash_password(req.password)

    log.info("signup: inserting new user into DB")
    user = User(
        full_name=req.full_name.strip(),
        email=req.email,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log.info("signup: writing session cookie for user_id=%s", user.id)
    # Log them in automatically
    request.session.clear()
    request.session["user_id"] = user.id

    log.info("signup: complete for user_id=%s", user.id)
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
    }

@auth_router.post("/login")
@limiter.limit("5/minute")
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    log.info("login: received request for email=%s", req.email)

    log.info("login: querying DB for user")
    user = db.query(User).filter(User.email == req.email).first()

    log.info("login: verifying password (bcrypt — expect ~200-500ms)")
    
    # Pre-computed bcrypt hash of "dummy"
    dummy_hash = b'$2b$12$Nq9rWjLq0nO2z8QZ1X7V3e8K5F6d9C6m3x5h9J2p5Nq9rWjLq0nO2'
    
    # Timing-safe validation
    is_valid = False
    if user:
        is_valid = verify_password(req.password, user.password_hash)
    else:
        verify_password(req.password, dummy_hash.decode('utf-8'))
        
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials"}
        )

    log.info("login: writing session cookie for user_id=%s", user.id)
    request.session.clear() # Fix session fixation
    request.session.clear()
    request.session["user_id"] = user.id

    log.info("login: complete for user_id=%s", user.id)
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
