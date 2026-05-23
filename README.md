# Smart Pest Backend

A FastAPI backend with JWT authentication, async PostgreSQL, and role-based access control.

## Tech Stack

- **Python 3.14+**
- **FastAPI** — web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0** (async) + **asyncpg** — database ORM and driver
- **Alembic** — database migrations
- **PostgreSQL 16** — primary database (via Docker)
- **JWT (HS256)** — access + refresh token authentication
- **bcrypt** — password hashing

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — package manager
- [Docker](https://www.docker.com/) — for running PostgreSQL

## Getting Started

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY`:

```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Start the database

```bash
docker compose up -d
```

### 4. Run migrations

```bash
uv run alembic upgrade head
```

### 5. (Optional) Seed the superuser

```bash
uv run python -m app.initial_data
```

### 6. Start the server

```bash
# Development (auto-reload)
fastapi dev app/main.py

# Production
fastapi run app/main.py
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://smart_pest:smart_pest@localhost:5432/smart_pest` |
| `SECRET_KEY` | JWT signing secret (64-char hex recommended) | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `FIRST_SUPERUSER_EMAIL` | Email for the seeded admin account | `admin@example.com` |
| `FIRST_SUPERUSER_PASSWORD` | Password for the seeded admin account | `changeme` |

---

## API Reference

### Auth — `/api/v1/auth`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/auth/register` | Register a new user | No |
| `POST` | `/auth/login` | Login and receive access + refresh tokens | No |
| `POST` | `/auth/refresh` | Exchange a refresh token for new tokens | No |
| `POST` | `/auth/logout` | Invalidate the current refresh token | Bearer |

### Users — `/api/v1/users`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/users/me` | Get current user profile | Bearer |
| `PATCH` | `/users/me` | Update current user profile | Bearer |
| `GET` | `/users/` | List all users (paginated) | Admin |
| `GET` | `/users/{user_id}` | Get a user by ID | Admin |
| `PATCH` | `/users/{user_id}` | Update any user | Admin |
| `DELETE` | `/users/{user_id}` | Delete a user | Admin |

---

## Project Structure

```
smart-pest-backend/
├── app/
│   ├── api/v1/          # Route handlers (auth, users)
│   ├── core/            # Security utilities and exceptions
│   ├── crud/            # Database operations
│   ├── db/              # SQLAlchemy engine and session
│   ├── models/          # ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── config.py        # Pydantic settings (reads from .env)
│   ├── initial_data.py  # Superuser seeding script
│   └── main.py          # FastAPI app entry point
├── alembic/             # Database migrations
├── docker-compose.yml   # PostgreSQL service
├── main.py              # Alternate entry point (python main.py)
└── pyproject.toml
```

---

## Database Migrations

```bash
# Apply all migrations
uv run alembic upgrade head

# Create a new migration after changing models
uv run alembic revision --autogenerate -m "description"

# Check current revision
uv run alembic current
```
