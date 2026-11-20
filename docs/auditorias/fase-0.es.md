# Auditoría — Fase 0 (arranque)

[English](fase-0.md) · **Español** · Fecha: 2026-11-20 · Rama: `feat/fase-0-arranque`

Leyenda: **[V]** verificado con comando y salida · **[S]** supuesto / no verificado.

## Entregable
- [V] `docker compose up --build -d` levanta `db`, `mailpit`, `backend` y `frontend`; los cuatro
  quedan `healthy`.
- [V] `GET /api/v1/health` → `200` con `"database": {"status": "ok", "provider": "supabase"}`
  (SELECT 1 real contra el Session pooler), tanto directo al backend como a través del rewrite
  de Next (`/api/*` → FastAPI).
- [V] Hot reload: un cambio en `frontend/app/page.tsx` se sirve sin reiniciar; un cambio en
  `backend/app` dispara `WatchFiles detected changes … Reloading`.
- [V] Contenedores sin root: backend `uid=10001(app)`, frontend `uid=1000(node)`.

## Lint y tipos
| Herramienta | Resultado |
|---|---|
| ruff check / ruff format --check | [V] sin errores |
| mypy (strict, plugin pydantic) | [V] `no issues found in 26 source files` |
| ESLint (next core-web-vitals + TS) | [V] sin errores |
| tsc --noEmit | [V] sin errores |
| Prettier --check | [V] todos los ficheros formateados |

## Tests y cobertura
- [V] Backend: **28 tests** en verde, cobertura total **97 %** (`services/` 100 %, `api/` 100 %).
  Ejecutados en el contenedor contra el Postgres local; `provider` = `postgresql` confirma que no
  se usó Supabase.
- [V] Frontend: **20 tests** Vitest en verde (contraste WCAG de los tokens, coincidencia
  `globals.css` ↔ `design-tokens.ts`, landmarks y h1 de la página provisional).
- [V] `next build` de producción correcto.

## Seguridad
| Comprobación | Resultado |
|---|---|
| bandit | [V] sin hallazgos |
| pip-audit | [V] `No known vulnerabilities found` |
| npm audit | [V] `found 0 vulnerabilities` |
| gitleaks (pre-commit, en Docker) | [V] sin secretos en los ficheros del repo |
| `.env` fuera del repo | [V] `git check-ignore` lo ignora; el hook `forbid-env-file` falla si se intenta añadir |
| Config: secretos ≥ 32, distintos, sin `change-me` | [V] tests unitarios |
| Health no filtra host/usuario/contraseña en error | [V] test unitario |
| CORS solo a orígenes configurados | [V] test unitario |
| Cabeceras: `nosniff`, `X-Frame-Options`, `Referrer-Policy` (API y web) | [V] tests + `curl -I` |
| Endpoints: solo `health` y `health/live` (públicos, sin datos) | [V] revisión manual |

## Accesibilidad y rendimiento
- Fase sin UI real. La página provisional tiene `lang="es"`, «Saltar al contenido», landmarks,
  un solo `h1` y foco visible ([V] test unitario de landmarks). axe/Lighthouse: [S] no ejecutados,
  se incorporan en la Fase 3 con Playwright.

## Problemas encontrados
| # | Problema | Estado |
|---|---|---|
| 1 | Puertos 8000 y 3000 ocupados por otro proyecto en la máquina | ✅ puertos del host configurables (`BACKEND_PORT`, `FRONTEND_PORT`) |
| 2 | pre-commit bloqueado por el Control de aplicaciones de Windows (WinError 4551) | ✅ se ejecuta en Docker (`scripts/pre-commit.ps1`) |
| 3 | pip-audit fallaba en el contenedor dev (caché en el bind mount) | ✅ `XDG_CACHE_HOME=/tmp/.cache` |
| 4 | Aviso de deprecación de Starlette sobre `httpx` en `TestClient` | ⏳ evaluar en Fase 1 |
| 5 | Sin CSP todavía (Next necesita nonces) | ⏳ Fase 3 / Fase 6 |
| 6 | Data API de Supabase activa | ⏳ acción manual del usuario |
| 7 | CI de GitHub Actions | ver estado en el PR |
