from __future__ import annotations

from datetime import timedelta

from src.core.security import create_access_token, verify_password
from src.services.user_service import UserInternal, UserService


class AuthService:
    def __init__(self, users: UserService) -> None:
        self._users = users

    def login(self, *, email: str, password: str) -> str:
        u: UserInternal | None = self._users.get_by_email(email)
        if not u or not verify_password(password, u.password_hash):
            raise ValueError("invalid_credentials")
        return create_access_token(u.id, expires_delta=timedelta(minutes=60))

    def register(self, *, username: str, email: str, password: str) -> UserInternal:
        return self._users.create(username=username, email=email, password=password)
