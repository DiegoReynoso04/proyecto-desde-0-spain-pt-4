# Active context

**Fase actual:** 0 — Arranque (rama `feat/fase-0-arranque`). PR abierto, pendiente de aprobación.

## En qué se está trabajando
- Fase 0 terminada: repo, Docker Compose, esqueletos backend/frontend, CI, pre-commit, docs.
- Esperando revisión del PR y CI en verde. **No hacer merge sin aprobación.**

## Próximos pasos (Fase 1 — Datos y autenticación)
1. Añadir dependencias justificadas: `alembic`, `pwdlib[argon2]`, `phonenumbers`,
   `email-validator`, librería de rate limit, `PyJWT`, `time-machine`.
2. Alembic con `version_table_schema=tallerya`; migración inicial con esquema, RLS en todas las
   tablas y `REVOKE ALL ON SCHEMA tallerya FROM anon, authenticated`.
3. Modelos: usuarios (roles), consentimientos (fecha + versión), tokens de refresh y de reset.
4. Registro/login alumno, login backoffice, refresh, logout, CSRF, rate limit + bloqueo, reset.
5. `scripts/seed.py` con `--confirm-remote` y `--reset`.

## Pendiente del usuario
- Desactivar la **Data API** en Supabase (Integrations → Data API): no se usa.
- Si quiere usar los puertos 8000/3000 por defecto, liberarlos o añadir `BACKEND_PORT`/`FRONTEND_PORT` a `.env`.
