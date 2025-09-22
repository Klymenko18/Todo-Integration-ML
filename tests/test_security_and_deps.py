from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import HTTPException

from src.core.dependencies import ensure_self_or_403, to_public
from src.core.security import create_access_token, decode_token, hash_password, verify_password
from src.services.user_service import UserInternal


def test_password_hashing():
    hpw = hash_password("secretpw")
    assert verify_password("secretpw", hpw)
    assert not verify_password("wrong", hpw)


def test_jwt_create_decode():
    tok = create_access_token("user-id-1", expires_delta=timedelta(minutes=1))
    payload = decode_token(tok)
    assert payload.sub == "user-id-1"
    assert isinstance(payload.exp, (int, float))


def test_ensure_self_or_403():
    cur = UserInternal(id="1", username="u", email="u@example.com", password_hash="x")
    ensure_self_or_403(user_id="1", current=cur)
    with pytest.raises(HTTPException) as ei:
        ensure_self_or_403(user_id="2", current=cur)
    assert ei.value.status_code == 403


def test_to_public():
    u = UserInternal(id="42", username="bob", email="b@e.com", password_hash="x")
    pub = to_public(u)
    assert pub.id == "42" and pub.username == "bob" and pub.email == "b@e.com"
