from __future__ import annotations

from types import SimpleNamespace

from fastapi import status


def test_ensure_self_allows(client, override_deps):
    class Svc:
        def get_by_id(self, uid: str):
            return SimpleNamespace(id=uid, username="u", email="u@e.com")

    with override_deps(
        get_current_user=lambda: SimpleNamespace(id="42"),
        get_user_service=lambda: Svc(),
    ):
        r = client.get("/users/42")
        assert r.status_code == status.HTTP_200_OK


def test_ensure_self_denies(client, override_deps):
    class Svc:
        def get_by_id(self, uid: str):
            return SimpleNamespace(id=uid, username="u", email="u@e.com")

    with override_deps(
        get_current_user=lambda: SimpleNamespace(id="42"),
        get_user_service=lambda: Svc(),
    ):
        r = client.get("/users/41")
        assert r.status_code == status.HTTP_403_FORBIDDEN
