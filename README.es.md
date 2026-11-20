# TallerYA

[English](README.md) · **Español**

Web de **talleres presenciales** de cocina, cerámica, música, pintura, dibujo y fotografía:
landing informativa, área de alumnos con reservas y pago simulado, y backoffice para el dueño
y los profesores.

> Estado: **Fase 0 (arranque)**. Hay esqueletos de backend y frontend que arrancan y un endpoint de
> salud. Las funcionalidades llegan en las fases 1–6.

## Requisitos
- Docker Desktop con WSL2 (Windows) o Docker Engine + Compose v2.
- Git. Opcional para trabajar fuera de Docker: Python 3.14 + [uv](https://docs.astral.sh/uv/), Node 24+.
- Un proyecto de Supabase (se usa **solo como PostgreSQL**).

## Puesta en marcha
1. Copia la plantilla y rellena los valores marcados con `<<< RELLENAR`:
   ```powershell
   Copy-Item .env.example .env
   ```
   - `DATABASE_URL`: en Supabase, **Connect → Session pooler** (puerto 5432), con
     `postgresql+psycopg://` y `?sslmode=require`. No uses el Transaction pooler (6543).
   - Genera cada secreto (≥ 32 caracteres, distintos entre sí):
     `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
2. Levanta todo:
   ```powershell
   docker compose up --build -d
   ```
3. Comprueba:
   | Servicio | URL |
   |---|---|
   | Web | http://localhost:3000 |
   | API health (Supabase `SELECT 1`) | http://localhost:8000/api/v1/health |
   | Docs de la API | http://localhost:8000/api/v1/docs |
   | Mailpit (correos capturados) | http://localhost:8025 |

   Si los puertos 8000 o 3000 están ocupados, define `BACKEND_PORT` y `FRONTEND_PORT` en `.env`.

`docker-compose.override.yml` se aplica automáticamente en desarrollo (hot reload con polling,
necesario en Windows). Para una ejecución tipo producción: `docker compose -f docker-compose.yml up --build -d`.

Las migraciones nunca se ejecutan al arrancar (para no tocar la BD remota sin querer):
`docker compose exec backend alembic upgrade head` (a partir de la Fase 1).

## Tests y calidad
Todos los tests usan el PostgreSQL local del contenedor `db` (`TEST_DATABASE_URL`); nunca Supabase.
```powershell
docker compose exec backend pytest --cov=app
```
```powershell
docker compose exec frontend npm test
```
Lint, tipos y auditorías de seguridad: ver la tabla de comandos en [CLAUDE.md](CLAUDE.md).
pre-commit (formato, gitleaks, bloqueo de `.env`) se ejecuta dentro de Docker en Windows:
```powershell
.\scripts\pre-commit.ps1 -Install
```

## Credenciales de seed
Llegan en la Fase 1 (`scripts/seed.py`). El admin inicial sale de `SEED_ADMIN_*` en `.env`.
Escribir en Supabase exige `--confirm-remote`; borrar datos exige además `--reset`.

## Supabase: pausa del plan gratuito
El plan gratuito **pausa el proyecto tras una semana sin actividad**. Síntoma: `/api/v1/health`
responde `503` con `"database": {"status": "error"}`. Para reactivarlo: entra en el
[panel de Supabase](https://supabase.com/dashboard), abre el proyecto y pulsa **Restore project**
(tarda unos minutos). Más detalles y endurecimiento en [docs/supabase.es.md](docs/supabase.es.md).

## Estructura
```
backend/     FastAPI (app/{core,models,schemas,repositories,services,api/v1,jobs}, tests/)
frontend/    Next.js App Router + Tailwind (app/, components/, lib/, tests/)
docs/        Documentación (EN + ES) y auditorías por fase
memory-bank/ Contexto del proyecto para el agente (ES)
scripts/     Utilidades (pre-commit en Docker)
tools/       Imágenes auxiliares
```
