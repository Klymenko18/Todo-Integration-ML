from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from src.core.dependencies import get_auth_service, get_user_service, to_public
from src.models.auth_models import Token, UserPublic
from src.services.auth_service import AuthService
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterPayload,
    users: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        u = users.create(username=payload.username, email=payload.email, password=payload.password)
        return to_public(u)
    except ValueError as e:
        msg = str(e)
        if msg in {"email_taken", "username_taken"}:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.post("/login", response_model=Token)
def login(
    email: EmailStr = Form(...),
    password: str = Form(...),
    auth: AuthService = Depends(get_auth_service),
) -> Token:
    try:
        access = auth.login(email=email, password=password)
        return Token(access_token=access)
    except ValueError as e:
        if str(e) == "invalid_credentials":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
            )
        raise
