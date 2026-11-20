# Audit — Phase 0 (bootstrap)

**English** · [Español](fase-0.es.md) · Date: 2026-11-20 · Branch: `feat/fase-0-arranque`

Legend: **[V]** verified with a command and its output · **[S]** assumed / not verified.

## Deliverable
- [V] `docker compose up --build -d` starts `db`, `mailpit`, `backend` and `frontend`; all four
  become `healthy`.
- [V] `GET /api/v1/health` → `200` with `"database": {"status": "ok", "provider": "supabase"}`
  (real SELECT 1 against the Session pooler), both directly and through the Next rewrite
  (`/api/*` → FastAPI).
- [V] Hot reload: a change to `frontend/app/page.tsx` is served without a restart; a change under
  `backend/app` triggers `WatchFiles detected changes … Reloading`.
- [V] Non-root containers: backend `uid=10001(app)`, frontend `uid=1000(node)`.

## Lint and types
| Tool | Result |
|---|---|
| ruff check / ruff format --check | [V] clean |
| mypy (strict, pydantic plugin) | [V] `no issues found in 26 source files` |
| ESLint (next core-web-vitals + TS) | [V] clean |
| tsc --noEmit | [V] clean |
| Prettier --check | [V] all files formatted |

## Tests and coverage
- [V] Backend: **28 tests** passing, total coverage **97 %** (`services/` 100 %, `api/` 100 %).
  Run in the container against local Postgres; `provider` = `postgresql` confirms Supabase was
  not used.
- [V] Frontend: **20 Vitest tests** passing (WCAG contrast of tokens, `globals.css` ↔
  `design-tokens.ts` match, landmarks and h1 of the placeholder page).
- [V] Production `next build` succeeds.

## Security
| Check | Result |
|---|---|
| bandit | [V] no findings |
| pip-audit | [V] `No known vulnerabilities found` |
| npm audit | [V] `found 0 vulnerabilities` |
| gitleaks (pre-commit, in Docker) | [V] no secrets in repo files |
| `.env` kept out of the repo | [V] `git check-ignore` ignores it; the `forbid-env-file` hook fails if it is added |
| Config: secrets ≥ 32 chars, distinct, no `change-me` | [V] unit tests |
| Health does not leak host/user/password on error | [V] unit test |
| CORS limited to configured origins | [V] unit test |
| Headers: `nosniff`, `X-Frame-Options`, `Referrer-Policy` (API and web) | [V] tests + `curl -I` |
| Endpoints: only `health` and `health/live` (public, no data) | [V] manual review |

## Accessibility and performance
- No real UI in this phase. The placeholder page has `lang="es"`, a skip link, landmarks, a single
  `h1` and visible focus ([V] landmarks unit test). axe/Lighthouse: [S] not run; added in Phase 3
  with Playwright.

## Issues found
| # | Issue | Status |
|---|---|---|
| 1 | Ports 8000 and 3000 taken by another project on the machine | ✅ configurable host ports (`BACKEND_PORT`, `FRONTEND_PORT`) |
| 2 | pre-commit blocked by Windows Application Control (WinError 4551) | ✅ runs in Docker (`scripts/pre-commit.ps1`) |
| 3 | pip-audit failed in the dev container (cache on the bind mount) | ✅ `XDG_CACHE_HOME=/tmp/.cache` |
| 4 | Starlette deprecation warning about `httpx` in `TestClient` | ⏳ evaluate in Phase 1 |
| 5 | No CSP yet (Next needs nonces) | ⏳ Phase 3 / Phase 6 |
| 6 | Supabase Data API still enabled | ⏳ manual action by the user |
| 7 | GitHub Actions CI | see PR status |
