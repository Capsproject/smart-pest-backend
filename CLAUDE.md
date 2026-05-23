# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv add <package>

# Run dev server (hot reload)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Seed first superuser (run once after migration)
uv run python -m app.initial_data

# Database migrations
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic history --verbose
```

## Architecture

FastAPI + SQLAlchemy (async) + SQLite (dev) with JWT authentication and role-based access.

```
app/
├── main.py              # FastAPI app; mounts all routers under /api/v1
├── config.py            # pydantic_settings Settings singleton (reads .env)
├── initial_data.py      # Seeds FIRST_SUPERUSER from .env; run once manually
├── db/
│   ├── base.py          # DeclarativeBase — import this in alembic/env.py, NOT session.py
│   └── session.py       # Async engine + AsyncSessionLocal + get_db() dependency
├── models/user.py       # User ORM model
├── schemas/
│   ├── user.py          # UserCreate, UserUpdate, UserUpdateAdmin, UserResponse, UserListResponse
│   └── token.py         # TokenResponse, RefreshRequest
├── crud/user.py         # Async DB functions (all take AsyncSession as first arg)
├── core/
│   ├── security.py      # hash_password, verify_password, create_access_token, create_refresh_token, decode_token
│   └── exceptions.py    # HTTPException factories: not_found, already_exists, credentials_invalid, forbidden
└── api/
    ├── deps.py          # Dependency chain: get_current_user → get_current_active_user → require_superuser
    └── v1/
        ├── auth.py      # POST /auth/register, /auth/login, /auth/refresh, /auth/logout
        └── users.py     # GET/PATCH /users/me; GET/PATCH/DELETE /users/, /users/{id} (superuser)
```

## Key Design Decisions

**JWT strategy:** Access tokens (30 min) + refresh tokens (7 days). Both carry a `type` claim (`"access"` / `"refresh"`) to prevent cross-use. Refresh tokens are stored as bcrypt hashes in `users.refresh_token_hash` — every `/auth/refresh` rotates the token; `/auth/logout` clears the hash.

**Dependency chain:** `get_current_user` decodes the JWT and loads the User row. `get_current_active_user` additionally checks `is_active`. `require_superuser` additionally checks `is_superuser`. Wire these via `Depends()` in route signatures.

**Alembic uses a sync URL:** `alembic/env.py` strips `+aiosqlite` from `DATABASE_URL` because Alembic runs synchronously. The app runtime keeps the async driver. When adding new models, import them in `alembic/env.py` alongside `app.models.user` so autogenerate detects them.

**Adding a new model:** Create `app/models/<name>.py` inheriting from `Base`, import it in `alembic/env.py`, then run `alembic revision --autogenerate`.

## Environment Variables

Copy `.env.example` to `.env`. Generate `SECRET_KEY` with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Key vars: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `FIRST_SUPERUSER_EMAIL`, `FIRST_SUPERUSER_PASSWORD`.
