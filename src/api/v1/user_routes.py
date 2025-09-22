from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from src.core.dependencies import ensure_self_or_403, get_current_user, get_user_service, to_public
from src.models.auth_models import UserPublic, UserUpdate
from src.services.user_service import UserInternal, UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserPublic])
def list_users(
    current: UserInternal = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
) -> list[UserPublic]:
    return svc.list()


@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(ensure_self_or_403)])
def get_user(
    user_id: str,
    svc: UserService = Depends(get_user_service),
) -> UserPublic:
    u = svc.get_by_id(user_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    return to_public(u)


@router.patch("/{user_id}", response_model=UserPublic, dependencies=[Depends(ensure_self_or_403)])
def update_user(
    user_id: str,
    payload: UserUpdate,
    svc: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        updated = svc.update(user_id, payload)
    except ValueError as e:
        code = str(e) or "conflict"
        if code in {"username_taken", "email_taken"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=code)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code)

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    return updated


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ensure_self_or_403)],
    response_class=Response,
)
def delete_user(
    user_id: str,
    svc: UserService = Depends(get_user_service),
) -> Response:
    ok = svc.delete(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
