from __future__ import annotations

from fastapi import status
from pydantic import BaseModel

from src.models.auth_models import UserPublic


def _fake_user(id_: str = "1", username: str = "loginuser", email: str = "login@example.com"):
    class U(BaseModel):
        id: str
        username: str
        email: str

    return U(id=id_, username=username, email=email)


def test_login_by_email_only(client, override_deps, monkeypatch):
    import src.api.v1.auth_routes as auth_routes

    monkeypatch.setattr(
        auth_routes,
        "to_public",
        lambda u: UserPublic(id=str(u.id), username=str(u.username), email=str(u.email)),
    )

    class FakeUsers:
        def create(self, username: str, email: str, password: str):
            return _fake_user(id_="42", username=username, email=email)

    class FakeAuth:
        def login(self, *, email: str, password: str) -> str:
            if email == "login@example.com" and password == "secretpw":
                return "jwt-token"
            raise ValueError("invalid_credentials")

    with override_deps(get_user_service=lambda: FakeUsers()):
        r = client.post(
            "/auth/register",
            json={"username": "loginuser", "email": "login@example.com", "password": "secretpw"},
        )
        assert r.status_code == status.HTTP_201_CREATED, r.text

    with override_deps(get_auth_service=lambda: FakeAuth()):
        rr = client.post("/auth/login", data={"email": "login@example.com", "password": "secretpw"})
        assert rr.status_code == status.HTTP_200_OK, rr.text
        body = rr.json()
        assert "access_token" in body and body["access_token"] == "jwt-token"


def test_login_invalid_credentials(client, override_deps):
    class FakeAuthBad:
        def login(self, *, email: str, password: str) -> str:
            raise ValueError("invalid_credentials")

    with override_deps(get_auth_service=lambda: FakeAuthBad()):
        rr = client.post("/auth/login", data={"email": "no@such.user", "password": "bad"})
        assert rr.status_code == status.HTTP_401_UNAUTHORIZED
        assert rr.json()["detail"] == "invalid_credentials"
