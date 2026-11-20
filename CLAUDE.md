# TallerYA — guía para Claude Code

TallerYA es la web de un negocio de talleres **presenciales** (cocina, cerámica, música, pintura,
dibujo, fotografía): landing informativa, área de alumnos con reservas y pago simulado, y backoffice
para el dueño y los profesores. Especificación completa: `PROMPT.md`. Contexto vivo: `memory-bank/`.

## Al empezar y al terminar
- **Al empezar cada sesión** lee `memory-bank/activeContext.md` y `memory-bank/progress.md`.
- **Al terminar una tarea** actualízalos. Las decisiones de arquitectura van a `memory-bank/decisions.md`.
- Trabajo por fases (ver `PROMPT.md` §10). No empieces una fase sin la aprobación de la anterior.

## Comandos (Windows + Docker Desktop, PowerShell)
| Qué | Comando |
|---|---|
| Levantar todo (dev, hot reload) | `docker compose up --build -d` |
| Producción local (sin override) | `docker compose -f docker-compose.yml up --build -d` |
| Health | `curl.exe http://localhost:8000/api/v1/health` |
| Migrar (Fase 1+) | `docker compose exec backend alembic upgrade head` |
| Seed local / remoto (Fase 1+) | `docker compose exec backend python scripts/seed.py [--confirm-remote] [--reset]` |
| Tests backend | `docker compose exec backend pytest --cov=app` |
| Lint/tipos backend | `docker compose exec backend ruff check .` · `ruff format --check .` · `mypy` |
| Seguridad backend | `docker compose exec backend bandit -c pyproject.toml -r app` · `pip-audit --skip-editable` |
| Tests frontend | `docker compose exec frontend npm test` |
| Lint/tipos frontend | `docker compose exec frontend npm run lint` · `npm run typecheck` · `npm run format:check` |
| Seguridad frontend | `docker compose exec frontend npm audit` |
| E2E + axe (Fase 3+) | `cd frontend; npx playwright test` |
| pre-commit (en Docker) | `.\scripts\pre-commit.ps1` · instalar hook: `.\scripts\pre-commit.ps1 -Install` |
| BD local en adminer | `docker compose --profile tools up -d adminer` |

Si 8000/3000 están ocupados, define `BACKEND_PORT` / `FRONTEND_PORT` (en `.env` o en la shell).

## Convenciones
- Estructura: `backend/app/{core,models,schemas,repositories,services,api/v1,jobs}`,
  `frontend/app/{(public),(auth),(alumno),backoffice}`, `frontend/{components,lib,tests}`.
- Python: snake_case, tipado estricto (mypy strict), ruff. TS: sin `any` sin justificar, Prettier.
- API REST versionada bajo `/api/v1`. El frontend llama a `/api/*` y Next lo reescribe a FastAPI.
- Git: Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`),
  una rama por fase `feat/fase-N-descripcion`, PR obligatorio con CI en verde.
  **Nunca hacer merge sin aprobación del usuario.**
- Documentos para personas en `docs/` en dos idiomas (`X.md` inglés, `X.es.md` español).
  `memory-bank/` y este archivo solo en español.

## Reglas de negocio críticas
- Estados de reserva: `PENDIENTE_PAGO → PAGADA → CONFIRMADA`; `PENDIENTE_PAGO → EXPIRADA | CANCELADA`;
  `PAGADA → CANCELADA` (solo admin, con o sin reembolso simulado, a elección del admin).
- `expires_at = min(created_at + 24 h, inicio del curso)`. Job cada 5 min + expiración perezosa al leer.
- Máximo **10 plazas** por curso (el admin puede bajarlo, nunca subirlo). Ocupan plaza
  `PENDIENTE_PAGO`, `PAGADA` y `CONFIRMADA`. Control con transacción + `SELECT … FOR UPDATE`.
- Una sola reserva activa por persona y curso (índice único parcial + validación en servicio).
  Si caduca o se cancela, puede volver a reservar.
- Solo usuarios registrados y con sesión reservan. Cursos de **una sola sesión**.
- Todos los cursos son **presenciales**: visible en landing, ficha del curso y correos.
- Importes en céntimos (entero). Fechas en UTC en BD; se muestran en `Europe/Madrid`.

## Accesibilidad (WCAG 2.2 AA) y paleta
- HTML semántico, landmarks, un `h1` por página, «Saltar al contenido», foco visible
  (anillo `cacao-700` 2 px + offset), formularios con label, `aria-invalid`, `aria-describedby`
  y resumen de errores. Objetivos táctiles ≥ 24×24 px (44×44 en móvil). `lang="es"`.
  `prefers-reduced-motion`. Mobile first (360 px). axe sin errores y Lighthouse a11y ≥ 95.
- Tokens: `ocre-400 #D99F59`, `ocre-300 #D99962`, `terracota-500 #A67153`, `cacao-700 #733F2D`,
  `crema-50 #F2F2F2`, `tinta-900 #1F1F1F` (`frontend/app/globals.css` + `lib/design-tokens.ts`).

| Par | Contraste | Uso |
|---|---|---|
| cacao-700 / crema-50 | 7,57:1 | ✅ texto normal |
| tinta-900 / ocre-400 | 7,11:1 | ✅ texto de botones ocre |
| terracota-500 / crema-50 | 3,67:1 | ⚠️ solo texto grande, iconos, bordes |
| blanco / ocre-400 | 2,32:1 | ❌ prohibido para texto |
| ocre-400 / crema-50 | 2,07:1 | ❌ nunca texto ni único borde |

`tests/unit/contrast.test.ts` falla si un par baja de 4,5:1 (texto) o 3:1 (grande/UI).

## Seguridad
- Contraseñas con Argon2id; nunca en texto plano, en logs ni en respuestas.
- Autorización por rol **y** por propiedad del recurso en el backend (no basta ocultar botones).
- JWT corto + refresh en cookies httpOnly/Secure/SameSite=Lax; CSRF en peticiones que modifican.
- Ningún secreto en el repo. `.env` **no se regenera ni se sobrescribe**; antes de cada commit
  comprueba `git status` (el hook `forbid-env-file` y gitleaks lo bloquean también).
- Nunca guardar números de tarjeta ni CVV (ni de prueba): solo referencia, importe, estado,
  fecha y como mucho los 4 últimos dígitos. Pagos detrás de `PaymentProvider`.
- Logs sin datos personales ni tokens.

## Base de datos
- Supabase **solo como PostgreSQL** (sin Supabase Auth/Storage/Data API/supabase-js ni sus claves).
- Session pooler (puerto 5432), driver `postgresql+psycopg://…?sslmode=require`, pool pequeño.
- Todo en el esquema `tallerya` (`search_path=tallerya`, tabla de versiones de Alembic incluida).
- Migraciones: `ENABLE ROW LEVEL SECURITY` en todas las tablas y `REVOKE ALL ON SCHEMA tallerya
  FROM anon, authenticated`. Migrar es un comando explícito, nunca al arrancar.
- **Tests siempre contra el Postgres local** (`TEST_DATABASE_URL`); `conftest.py` aborta si apunta a Supabase.
- Seed remoto solo con `--confirm-remote`; borrar datos solo con `--reset`.

## Definición de terminado
Tests en verde · lint y tipos limpios · accesibilidad revisada si hay UI · docs y `memory-bank/`
actualizados · auditoría de fase en `docs/auditorias/` · PR con CI en verde.

## Qué no hacer
- No añadir dependencias sin justificarlas (anótalo en `decisions.md`).
- No desactivar ni saltarse tests; no saltarse fases; no `any` en TypeScript sin motivo.
- No conectar tests a Supabase, no tocar `.env`, no hacer merge sin aprobación.
