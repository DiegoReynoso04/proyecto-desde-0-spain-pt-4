# TallerYA

**English** · [Español](README.es.md)

Website for **in-person workshops** in cooking, ceramics, music, painting, drawing and
photography: an informational landing page, a student area with bookings and simulated payment,
and a back office for the owner and the teachers.

> Status: **Phase 0 (bootstrap)**. Backend and frontend skeletons start up and expose a health
> endpoint. Features arrive in phases 1–6.

## Requirements
- Docker Desktop with WSL2 (Windows) or Docker Engine + Compose v2.
- Git. Optional, to work outside Docker: Python 3.14 + [uv](https://docs.astral.sh/uv/), Node 24+.
- A Supabase project (used **only as PostgreSQL**).

## Getting started
1. Copy the template and fill in the values marked `<<< RELLENAR`:
   ```powershell
   Copy-Item .env.example .env
   ```
   - `DATABASE_URL`: in Supabase, **Connect → Session pooler** (port 5432), using
     `postgresql+psycopg://` and `?sslmode=require`. Do not use the Transaction pooler (6543).
   - Generate each secret (≥ 32 characters, all different):
     `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
2. Start everything:
   ```powershell
   docker compose up --build -d
   ```
3. Check:
   | Service | URL |
   |---|---|
   | Website | http://localhost:3000 |
   | API health (Supabase `SELECT 1`) | http://localhost:8000/api/v1/health |
   | API docs | http://localhost:8000/api/v1/docs |
   | Mailpit (captured emails) | http://localhost:8025 |

   If ports 8000 or 3000 are taken, set `BACKEND_PORT` and `FRONTEND_PORT` in `.env`.

`docker-compose.override.yml` is applied automatically in development (hot reload with polling,
needed on Windows). For a production-like run: `docker compose -f docker-compose.yml up --build -d`.

Migrations never run on startup (so the remote database is never changed by accident):
`docker compose exec backend alembic upgrade head` (from Phase 1 on).

## Tests and quality
All tests use the local PostgreSQL in the `db` container (`TEST_DATABASE_URL`), never Supabase.
```powershell
docker compose exec backend pytest --cov=app
```
```powershell
docker compose exec frontend npm test
```
Lint, type checks and security audits: see the command table in [CLAUDE.md](CLAUDE.md) (Spanish).
pre-commit (formatting, gitleaks, `.env` guard) runs inside Docker on Windows:
```powershell
.\scripts\pre-commit.ps1 -Install
```

## Seed credentials
Coming in Phase 1 (`scripts/seed.py`). The initial admin comes from `SEED_ADMIN_*` in `.env`.
Writing to Supabase requires `--confirm-remote`; deleting data also requires `--reset`.

## Supabase: free plan pausing
The free plan **pauses the project after one week of inactivity**. Symptom: `/api/v1/health`
returns `503` with `"database": {"status": "error"}`. To reactivate it, open the
[Supabase dashboard](https://supabase.com/dashboard), select the project and click
**Restore project** (takes a few minutes). More details and hardening in [docs/supabase.md](docs/supabase.md).

## Structure
```
backend/     FastAPI (app/{core,models,schemas,repositories,services,api/v1,jobs}, tests/)
frontend/    Next.js App Router + Tailwind (app/, components/, lib/, tests/)
docs/        Documentation (EN + ES) and per-phase audits
memory-bank/ Project context for the coding agent (ES)
scripts/     Utilities (pre-commit in Docker)
tools/       Helper images
```
