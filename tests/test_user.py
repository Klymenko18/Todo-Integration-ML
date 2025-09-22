from __future__ import annotations

from fastapi import status

from src.models.auth_models import UserPublic


def _stub_user_public(i: int = 1) -> UserPublic:
    return UserPublic(id=str(i), username=f"user{i}", email=f"user{i}@ex.com")


def test_users_list_and_get_update_delete(client, override_deps, monkeypatch):
    import src.api.v1.user_routes as user_routes

    monkeypatch.setattr(
        user_routes,
        "to_public",
        lambda u: UserPublic(id=str(u["id"]), username=u["username"], email=u["email"]),
    )

    with override_deps(get_current_user=lambda: object(), ensure_self_or_403=lambda: None):

        class FakeUsersSvc:
            def __init__(self):
                self._data = {"1": {"id": "1", "username": "user1", "email": "user1@ex.com"}}

            def list(self):
                return [UserPublic(**v) for v in self._data.values()]

            def get_by_id(self, uid: str):
                return self._data.get(uid)

            def update(self, uid: str, payload):
                if payload.username == "taken":
                    raise ValueError("username_taken")
                if uid not in self._data:
                    return None
                self._data[uid]["username"] = payload.username or self._data[uid]["username"]
                return UserPublic(**self._data[uid])

            def delete(self, uid: str) -> bool:
                return bool(self._data.pop(uid, None))

        svc = FakeUsersSvc()

        with override_deps(get_user_service=lambda: svc):
            r = client.get("/users")
            assert r.status_code == status.HTTP_200_OK
            assert r.json()[0]["username"] == "user1"

        with override_deps(get_user_service=lambda: svc):
            r = client.get("/users/1")
            assert r.status_code == status.HTTP_200_OK
            assert r.json()["email"] == "user1@ex.com"

        with override_deps(get_user_service=lambda: svc):
            r = client.get("/users/404")
            assert r.status_code == status.HTTP_404_NOT_FOUND

        with override_deps(get_user_service=lambda: svc):
            r = client.patch("/users/1", json={"username": "newname"})
            assert r.status_code == status.HTTP_200_OK
            assert r.json()["username"] == "newname"

        with override_deps(get_user_service=lambda: svc):
            r = client.patch("/users/1", json={"username": "taken"})
            assert r.status_code == status.HTTP_409_CONFLICT
            assert r.json()["detail"] in {"username_taken", "email_taken"}

        with override_deps(get_user_service=lambda: svc):
            r = client.patch("/users/404", json={"username": "validname"})
            assert r.status_code == status.HTTP_404_NOT_FOUND

        with override_deps(get_user_service=lambda: svc):
            r = client.delete("/users/1")
            assert r.status_code == status.HTTP_204_NO_CONTENT

        with override_deps(get_user_service=lambda: svc):
            r = client.delete("/users/1")
            assert r.status_code == status.HTTP_404_NOT_FOUND
