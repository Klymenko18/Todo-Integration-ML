from __future__ import annotations

import threading
from dataclasses import dataclass

from passlib.hash import bcrypt


@dataclass(frozen=True)
class UserInternal:
    id: str
    username: str
    email: str
    password_hash: str


class UserService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_id: dict[str, UserInternal] = {}
        self._by_username: dict[str, str] = {}
        self._by_email: dict[str, str] = {}
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return str(self._counter)

    def create(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
        password_plain: str | None = None,
        password_hash: str | None = None,
        payload: object | None = None,
    ) -> UserInternal:
        if payload is not None:
            username = username or getattr(payload, "username", None)
            email = email or getattr(payload, "email", None)
            password = password or getattr(payload, "password", None)
            password_plain = password_plain or getattr(payload, "password_plain", None)
            password_hash = password_hash or getattr(payload, "password_hash", None)

        if not username or not email:
            raise ValueError("username and email are required")

        raw = password or password_plain
        if raw and not password_hash:
            password_hash = bcrypt.hash(raw)
        if not password_hash:
            raise ValueError("password or password_hash is required")

        with self._lock:
            if username in self._by_username:
                raise ValueError("username_taken")
            if email in self._by_email:
                raise ValueError("email_taken")

            uid = self._next_id()
            user = UserInternal(id=uid, username=username, email=email, password_hash=password_hash)

            self._by_id[uid] = user
            self._by_username[username] = uid
            self._by_email[email] = uid
            return user

    def get_by_id(self, uid: str) -> UserInternal | None:
        with self._lock:
            return self._by_id.get(uid)

    def get_by_username(self, username: str) -> UserInternal | None:
        with self._lock:
            uid = self._by_username.get(username)
            return self._by_id.get(uid) if uid else None

    def get_by_email(self, email: str) -> UserInternal | None:
        with self._lock:
            uid = self._by_email.get(email)
            return self._by_id.get(uid) if uid else None

    def authenticate(self, identifier: str, password: str) -> UserInternal | None:
        user = self.get_by_username(identifier) or self.get_by_email(identifier)
        if not user:
            return None
        if bcrypt.verify(password, user.password_hash):
            return user
        return None
