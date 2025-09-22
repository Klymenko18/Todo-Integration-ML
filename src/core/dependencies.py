from __future__ import annotations

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer

from src.core.security import decode_token
from src.models.auth_models import UserPublic
from src.services.auth_service import AuthService
from src.services.todo_service import InMemoryTaskService
from src.services.user_service import UserInternal, UserService

_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_user_svc_singleton: UserService | None = None
_auth_svc_singleton: AuthService | None = None
_todo_svc_singleton: InMemoryTaskService | None = None


def get_user_service() -> UserService:
    global _user_svc_singleton
    if _user_svc_singleton is None:
        _user_svc_singleton = UserService()
    return _user_svc_singleton


def get_auth_service(
    users: UserService = Depends(get_user_service),
) -> AuthService:
    global _auth_svc_singleton
    if _auth_svc_singleton is None:
        _auth_svc_singleton = AuthService(users)
    return _auth_svc_singleton


def get_todo_service() -> InMemoryTaskService:
    global _todo_svc_singleton
    if _todo_svc_singleton is None:
        _todo_svc_singleton = InMemoryTaskService()
    return _todo_svc_singleton


def get_current_user(
    token: str = Depends(_oauth2),
    users: UserService = Depends(get_user_service),
) -> UserInternal:
    try:
        payload = decode_token(token)
        u = users.get_by_id(payload.sub)
        if not u:
            raise ValueError("user not found")
        return u
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def ensure_self_or_403(
    user_id: str = Path(...),
    current: UserInternal = Depends(get_current_user),
) -> None:
    if current.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


def to_public(u: UserInternal) -> UserPublic:
    return UserPublic(id=u.id, username=u.username, email=u.email)
