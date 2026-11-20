# Progress

## Hecho
### Fase 0 — Arranque (2026-11-20)
- `.gitignore` con `.env` (primer commit en `main`) y `.gitattributes` (LF; CRLF para `.ps1/.bat/.cmd`).
- Backend FastAPI: config validada, motor SQLAlchemy con `search_path`, `/api/v1/health`
  (SELECT 1) y `/api/v1/health/live`, cabeceras de seguridad, CORS restringido. 28 tests, 97 %.
- Frontend Next.js 16.4 + Tailwind 4 con tokens de la paleta, página provisional accesible,
  rewrite `/api/*` → FastAPI, test de contraste de tokens. 20 tests Vitest.
- Docker Compose: db, mailpit, backend, frontend (+ adminer y precommit en perfil `tools`).
  Hot reload verificado en ambos servicios.
- CI GitHub Actions, pre-commit (gitleaks + forbid-env-file + ruff), CLAUDE.md, memory-bank, READMEs.

## Falta
- Fases 1–6 (ver `PROMPT.md` §10).
- Servicio `scheduler` (Fase 2). Playwright + axe (Fase 3). CSP (Fases 3/6).

## Bugs / incidencias relevantes
- pre-commit bloqueado en Windows por el Control de aplicaciones (WinError 4551) → se ejecuta en Docker.
- `pip-audit` en el contenedor dev fallaba porque su caché caía en `/app` (bind mount con permisos
  de Windows) → `XDG_CACHE_HOME=/tmp/.cache` en la imagen.
- Aviso de Starlette: «Using httpx with starlette.testclient is deprecated; install httpx2».
  Pendiente de evaluar en la Fase 1 (el prompt pide httpx).
