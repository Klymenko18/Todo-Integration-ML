from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

try:
    from src.core.settings import get_settings
except Exception:
    get_settings = None

try:
    from src.models.auth_models import TokenPayload
except Exception:
    from pydantic import BaseModel

    class TokenPayload(BaseModel):
        sub: str
        exp: int | float


_SETTINGS = get_settings() if callable(get_settings) else None
SECRET_KEY: str = (
    _SETTINGS.secret_key
    if _SETTINGS and getattr(_SETTINGS, "secret_key", None)
    else os.getenv("SECRET_KEY", "dev-secret")
)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _pwd.verify(password, hashed)


def create_access_token(
    subject: str | dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: dict[str, Any] = {"exp": expire}
    if isinstance(subject, str):
        payload["sub"] = subject
    else:
        payload.update(subject)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    sub = data.get("sub")
    exp = data.get("exp")
    if not sub or not exp:
        raise jwt.InvalidTokenError("Token is missing required claims: sub/exp")
    if isinstance(exp, datetime):
        exp_val: int | float = int(exp.timestamp())
    else:
        exp_val = exp
    return TokenPayload.model_validate({"sub": sub, "exp": exp_val})


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "TokenPayload",
]
