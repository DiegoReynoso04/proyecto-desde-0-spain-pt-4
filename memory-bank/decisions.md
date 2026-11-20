# Registro de decisiones (ADR breves)

Formato: fecha · decisión · motivo · alternativas descartadas.

## 2026-11-20 — Supuestos de negocio confirmados por el usuario (§11)
- Notificaciones: casilla opcional; la privacidad es obligatoria; los transaccionales se envían siempre.
- Duplicados: tras caducar o cancelarse, la persona puede volver a reservar el mismo curso.
- Las reservas `PENDIENTE_PAGO` ocupan plaza durante su plazo.
- **Cursos de una sola sesión** (inicio + duración). No se crea `course_sessions`.
- Límite de 10 plazas para todos los cursos; el admin puede bajarlo, no subirlo.
- Cancelación tras el pago: solo el admin.
- **Reembolso: al cancelar una reserva pagada, el admin elige si hay reembolso simulado o no.**
  (El usuario eligió esta opción frente a «siempre reembolso total».)

## 2026-11-20 — Estructura en la raíz del repo
- Decisión: `backend/`, `frontend/`, `docker-compose*.yml`, etc. en la raíz (la raíz hace de `tallerya/`).
- Motivo: `.env` ya está en la raíz; Docker lo lee sin rutas extra. Confirmado por el usuario.

## 2026-11-20 — Python 3.14 + uv
- Decisión: imagen `python:3.14-slim`, dependencias con `uv` y `uv.lock`.
- Motivo: 3.14 es la versión estable instalada localmente y cumple «3.12+»; uv da lockfile
  reproducible y builds rápidos. Alternativa: pip + requirements.txt (sin lock con hashes cómodo).

## 2026-11-20 — Node 26 LTS en Docker y CI
- Decisión: `node:26-alpine` (LTS actual). En local hay Node 24, compatible (`engines >= 24`).

## 2026-11-20 — Next.js 16.4 con Turbopack y polling
- Decisión: mantener Turbopack (por defecto en 16.x) con `watchOptions.pollIntervalMs` cuando
  `WATCHPACK_POLLING=true`. Verificado: el hot reload funciona en Docker sobre Windows.
- `output: "standalone"` para la imagen de producción multi-stage.
- Fuentes del sistema (sin `next/font/google`) para que el build no dependa de red.

## 2026-11-20 — Health en dos endpoints
- `/api/v1/health`: `SELECT 1`, 200/503, latencia, proveedor (`supabase`/`postgresql`).
  En error solo devuelve el tipo de excepción (no host, usuario ni mensaje del driver).
- `/api/v1/health/live`: sin BD; lo usa el healthcheck de Docker para que una pausa de Supabase
  no tumbe el arranque del frontend.

## 2026-11-20 — Docs de la API bajo `/api/v1/docs`
- Motivo: así se alcanzan también a través del rewrite de Next. Desactivadas en producción.

## 2026-11-20 — Validación estricta de la configuración
- Secretos ≥ 32 caracteres, distintos entre sí y distintos de valores de ejemplo.
- En producción: `DEBUG=false`, `COOKIE_SECURE=true`, CORS sin `*`.
- `COURSE_MAX_CAPACITY` ≤ 10; `DB_SCHEMA` identificador válido y distinto de `public`.

## 2026-11-20 — `search_path` por evento `connect`
- Se ejecuta `SET search_path TO tallerya` en autocommit en cada conexión nueva.
- Motivo: no depender de que el pooler de Supabase acepte el parámetro `options` de arranque,
  y que el `SET` no se pierda con un rollback (test de regresión incluido).

## 2026-11-20 — pre-commit dentro de Docker
- Problema: el Control de aplicaciones de Windows (WinError 4551) bloquea de forma intermitente
  los ejecutables que pre-commit instala en su caché (hooks de Python y gitleaks).
- Decisión: servicio `precommit` (perfil `tools`) + `scripts/pre-commit.ps1`, que también instala un
  hook de git que lo invoca. No se toca la política de seguridad de Windows.
- Detección de secretos: **gitleaks** (sin baseline que mantener) + hook propio `forbid-env-file`.
- mypy, ESLint, tsc y tests no van en pre-commit (lentos, necesitan dependencias): van en la CI.

## 2026-11-20 — Puertos del host configurables
- `BACKEND_PORT`, `FRONTEND_PORT`, `ADMINER_PORT` con valores por defecto 8000/3000/8080.
- Motivo: en la máquina del usuario 8000 y 3000 los usa otro proyecto.

## 2026-11-20 — `env_file: .env` en todos los servicios
- Se sigue el requisito del prompt. Riesgo asumido: `db` y `frontend` reciben variables que no usan
  (incluidos secretos del backend) solo en el entorno del contenedor; nunca llegan al navegador
  (solo las `NEXT_PUBLIC_*` se incrustan en el build). El `db` fuerza `TZ=UTC`.
  Revisar en la Fase 6 si se separan ficheros de entorno por servicio.
