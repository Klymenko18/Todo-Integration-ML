from __future__ import annotations

from datetime import timedelta

from src.core.security import create_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    h = hash_password("secret")
    assert isinstance(h, str) and h != "secret"
    assert verify_password("secret", h)
    assert not verify_password("wrong", h)


def test_create_access_token():
    t = create_access_token("user-id", expires_delta=timedelta(seconds=1))
    assert isinstance(t, str) and len(t) > 10
