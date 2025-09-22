from __future__ import annotations

from types import SimpleNamespace

from fastapi import status

from src.models.auth_models import UserPublic


def test_register_and_conflict(client, override_deps, monkeypatch):
    import src.api.v1.auth_routes as auth_routes

    monkeypatch.setattr(
        auth_routes,
        "to_public",
        lambda u: UserPublic(id=str(u.id), username=str(u.username), email=str(u.email)),
    )

    class FakeUsers:
        def __init__(self):
            self._taken = False

        def create(self, username: str, email: str, password: str):
            if self._taken:
                raise ValueError("email_taken")
            self._taken = True
            return SimpleNamespace(id="1", username=username, email=email)

    svc = FakeUsers()

    with override_deps(get_user_service=lambda: svc):
        p = {"username": "user1", "email": "u1@example.com", "password": "secretpw"}
        r1 = client.post("/auth/register", json=p)
        assert r1.status_code == status.HTTP_201_CREATED, r1.text

        r2 = client.post("/auth/register", json=p)
        assert r2.status_code == status.HTTP_409_CONFLICT
        assert r2.json()["detail"] == "email_taken"
