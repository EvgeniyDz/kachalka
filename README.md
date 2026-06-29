# Kachalka

Kachalka is a Ukrainian-first workout tracking application for recording training sessions, reviewing progress, detecting personal records, and exploring strength analytics.

## Project Structure

- `backend/` - FastAPI, SQLAlchemy, PostgreSQL, and Alembic.
- `frontend/` - Vue 3, TypeScript, Vite, Pinia, Vue Router, and vue-i18n.
- `docker-compose.yml` - local PostgreSQL, backend, and frontend services.
- `scripts/` - local code-quality checks.

## Quick Start

### Full Stack With Docker

```powershell
docker compose up --build
```

The frontend is available at `http://localhost:5173`.
The API is available at `http://localhost:8000`.
Interactive API documentation is available at `http://localhost:8000/docs`.

The backend container waits for PostgreSQL, applies Alembic migrations, seeds the default exercise catalog, and then starts FastAPI.

To stop the stack:

```powershell
docker compose down
```

### Local Backend And Frontend

Use this mode when you want to run PostgreSQL in Docker but run backend/frontend directly on your machine.

```powershell
docker compose up -d postgres
```

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## Quality Checks

### Backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

### Frontend

```powershell
cd frontend
npm run lint
npm run test
npm run build
```
