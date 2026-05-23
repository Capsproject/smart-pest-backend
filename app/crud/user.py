from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import bcrypt

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserUpdateAdmin


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def count_users(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def create_user(db: AsyncSession, schema: UserCreate) -> User:
    user = User(
        email=schema.email,
        hashed_password=hash_password(schema.password),
        full_name=schema.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession, user: User, schema: UserUpdate | UserUpdateAdmin
) -> User:
    data = schema.model_dump(exclude_unset=True)
    if "password" in data:
        user.hashed_password = hash_password(data.pop("password"))
    for field, value in data.items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def update_refresh_token(
    db: AsyncSession, user: User, token: str | None
) -> None:
    if token is None:
        user.refresh_token_hash = None
    else:
        user.refresh_token_hash = bcrypt.hashpw(token.encode(), bcrypt.gensalt()).decode()
    db.add(user)
    await db.commit()
