# System patterns

## Arquitectura
```
Navegador ──▶ Next.js (frontend:3000) ──rewrite /api/*──▶ FastAPI (backend:8000) ──▶ Supabase Postgres
                                                              │                        (esquema tallerya)
                                                              ├──▶ Mailpit (SMTP dev)
scheduler (misma imagen que backend, Fase 2) ─────────────────┘
db (Postgres 17 local) ◀── solo tests
```
- Mismo origen para el navegador (cookies first-party): el frontend nunca llama al backend por CORS.
- Backend por capas: `api/v1` (routers, validación Pydantic, auth) → `services` (reglas de negocio,
  transacciones) → `repositories` (acceso SQLAlchemy) → `models`. `schemas` = DTOs Pydantic.
- Configuración única en `app/core/config.py` (pydantic-settings), validada al arrancar.
- Motor SQLAlchemy en `app/core/db.py`: `pool_pre_ping`, pool pequeño, `search_path` fijado en
  cada conexión (en autocommit para que sobreviva a rollbacks).

## Máquina de estados de reserva
```
PENDIENTE_PAGO ──pago OK──▶ PAGADA ──admin inscribe──▶ CONFIRMADA
      │                        │
      ├──vence──▶ EXPIRADA     └──admin cancela (con/sin reembolso)──▶ CANCELADA
      └──alumno cancela──▶ CANCELADA
```
- Las transiciones se validan en un único servicio; cualquier otra → error de dominio (409).
- `CONFIRMADA` también puede cancelarla el admin (mismo flujo que `PAGADA`) — *supuesto a
  confirmar en Fase 2*.

## Patrones
- **PaymentProvider** (interfaz): `create_payment`, `confirm`, `refund`. Implementación
  `SimulatedPaymentProvider`; futuro Stripe/Redsys sin tocar reservas.
- **Control de plazas**: transacción + `SELECT … FOR UPDATE` sobre el curso + índice único parcial
  `(user_id, course_id) WHERE status IN ('PENDIENTE_PAGO','PAGADA','CONFIRMADA')`.
- **Expiración**: job periódico + expiración perezosa al leer.
- **Notificaciones**: servicio único que decide transaccional vs. opcional (consentimiento).
- **Auditoría**: registro de acciones del backoffice (quién, qué, cuándo).
- **Health**: `/api/v1/health` (SELECT 1, 503 si falla, sin exponer detalles) y
  `/api/v1/health/live` (sin BD, usado por el healthcheck de Docker).
