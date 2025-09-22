from __future__ import annotations

from datetime import timedelta

from src.core.security import create_access_token
from src.services.user_service import UserInternal, UserService


class AuthService:
    def __init__(self, users: UserService) -> None:
        self._users = users

    def login(self, email: str, password: str) -> str:
        u: UserInternal | None = self._users.authenticate(email, password)
        if not u:
            raise ValueError("invalid_credentials")
        return create_access_token(u.id, expires_delta=timedelta(minutes=60))
