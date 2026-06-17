"""User auth: signup, login, current user. (Integration connect lives in oauth.py.)"""
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, security
from ..services import mock_data

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.TokenResponse, status_code=201)
def signup(body: schemas.SignupRequest):
    if any(u["email"] == body.email for u in mock_data.USERS.values()):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    uid = str(uuid4())
    mock_data.USERS[uid] = {"id": uid, "name": body.name, "email": body.email,
                            "password": security.hash_password(body.password)}
    return schemas.TokenResponse(
        access_token=security.create_access_token(uid, body.name),
        user=schemas.UserPublic(id=uid, name=body.name, email=body.email))


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest):
    user = next((u for u in mock_data.USERS.values() if u["email"] == body.email), None)
    if not user or not security.verify_password(body.password, user["password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return schemas.TokenResponse(
        access_token=security.create_access_token(user["id"], user["name"]),
        user=schemas.UserPublic(id=user["id"], name=user["name"], email=user["email"]))


@router.get("/me")
def me(user: dict = Depends(security.get_current_user)):
    return user
