from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import get_current_active_user, get_db, require_superuser
from app.core.exceptions import not_found
from app.models.user import User
from app.schemas.user import UserListResponse, UserResponse, UserUpdate, UserUpdateAdmin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    schema: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    return await crud.user.update_user(db, current_user, schema)


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
) -> UserListResponse:
    users = await crud.user.get_users(db, skip=skip, limit=limit)
    total = await crud.user.count_users(db)
    return UserListResponse(items=users, total=total, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
) -> User:
    user = await crud.user.get_user_by_id(db, user_id)
    if not user:
        raise not_found("User")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    schema: UserUpdateAdmin,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
) -> User:
    user = await crud.user.get_user_by_id(db, user_id)
    if not user:
        raise not_found("User")
    return await crud.user.update_user(db, user, schema)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> None:
    if user_id == current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    user = await crud.user.get_user_by_id(db, user_id)
    if not user:
        raise not_found("User")
    await crud.user.delete_user(db, user)
