# Tech context

## Versiones (verificadas el 2026-11-20)
| Pieza | Versión |
|---|---|
| Python (imagen `python:3.14-slim`) | 3.14.10 |
| uv | 0.12.21 |
| FastAPI / uvicorn / SQLAlchemy / psycopg | ver `backend/uv.lock` |
| Node (imagen `node:26-alpine`, LTS) | 26.13 (local: 24.18) |
| Next.js / React | 16.4.6 / 19.3.0 |
| Tailwind CSS | 4.3.3 (tokens en `@theme`, loader `@tailwindcss/turbopack`) |
| Vitest | 5.1 |
| PostgreSQL local | 17 (alpine) |
| Mailpit | 1.34 |
| Docker / Compose | 29.7 / 5.5 (Docker Desktop, WSL2) |

## Docker
- `docker-compose.yml`: `db`, `mailpit`, `backend` (target `prod`), `frontend` (target `prod`),
  `adminer` y `precommit` (perfil `tools`).
- `docker-compose.override.yml` (dev, se aplica solo): targets `dev`, código montado,
  `WATCHFILES_FORCE_POLLING` (uvicorn) y `WATCHPACK_POLLING` + `watchOptions.pollIntervalMs` (Next).
- `node_modules` y `.next` como volúmenes anónimos (binarios Linux, no los de Windows).
- Imágenes con usuario no root (`app` uid 10001, `node` uid 1000).
- `scheduler` se añade en la Fase 2.

## Variables de entorno
- `.env` en la raíz (no se commitea, no se sobrescribe). Plantilla: `.env.example`.
- Obligatorias para el backend: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`,
  `PASSWORD_RESET_SECRET_KEY`, `CSRF_SECRET_KEY`, `PAYMENT_SIMULATION_SECRET` (≥ 32 caracteres,
  distintos entre sí, nunca `change-me`).
- Puertos del host configurables: `BACKEND_PORT`, `FRONTEND_PORT`, `POSTGRES_PORT`,
  `MAILPIT_UI_PORT`, `ADMINER_PORT`.
- `NEXT_PUBLIC_*` y `API_INTERNAL_URL` se pasan como build args al frontend.

## Herramientas
- pre-commit se ejecuta **en Docker** (`scripts/pre-commit.ps1`): el Control de aplicaciones de
  Windows bloquea los ejecutables de la caché de pre-commit en el host. En CI corre nativo.
- CI (`.github/workflows/ci.yml`): pre-commit, backend (Postgres de servicio), frontend, imágenes Docker.

## Comandos
Ver tabla en `CLAUDE.md`.
