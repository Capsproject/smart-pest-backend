import asyncio

from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_superuser == True))  # noqa: E712
        superuser = result.scalar_one_or_none()
        if superuser:
            print(f"Superuser already exists: {superuser.email}")
            return
        user = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        print(f"Superuser created: {settings.FIRST_SUPERUSER_EMAIL}")


if __name__ == "__main__":
    asyncio.run(main())
