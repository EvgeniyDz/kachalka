# Kachalka

Kachalka is a Ukrainian-first workout tracking application for recording training sessions, reviewing progress, detecting personal records, and exploring strength analytics.

## Project Structure

- `backend/` - FastAPI, SQLAlchemy, PostgreSQL, and Alembic.
- `frontend/` - Vue 3, TypeScript, Vite, Pinia, Vue Router, and vue-i18n.
- `docker-compose.yml` - local PostgreSQL service.
- `scripts/` - local code-quality checks.

## Quick Start

### Database

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
```

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend is available at `http://localhost:5173`.

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
npm run build```

