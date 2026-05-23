import bcrypt
import jwt
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import get_current_active_user, get_db
from app.config import settings
from app.core.exceptions import already_exists, credentials_invalid, forbidden
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User
from app.schemas.token import RefreshRequest, TokenResponse
from app.schemas.user import LoginRequest, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(schema: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    if await crud.user.get_user_by_email(db, schema.email):
        raise already_exists("Email")
    return await crud.user.create_user(db, schema)


@router.post("/login", response_model=TokenResponse)
async def login(schema: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await crud.user.get_user_by_email(db, schema.email)
    if not user or not verify_password(schema.password, user.hashed_password):
        raise credentials_invalid()
    if not user.is_active:
        raise forbidden("Inactive user")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    await crud.user.update_refresh_token(db, user, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(schema: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    exc = credentials_invalid()
    try:
        payload = jwt.decode(
            schema.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise exc
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise exc
    user = await crud.user.get_user_by_id(db, user_id)
    if not user or not user.refresh_token_hash:
        raise exc
    if not bcrypt.checkpw(schema.refresh_token.encode(), user.refresh_token_hash.encode()):
        raise exc
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    await crud.user.update_refresh_token(db, user, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await crud.user.update_refresh_token(db, current_user, None)
