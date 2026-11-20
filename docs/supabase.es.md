# Supabase: uso y endurecimiento

[English](supabase.md) · **Español**

TallerYA usa Supabase **solo como PostgreSQL gestionado**. No se usan Supabase Auth, Storage, Edge
Functions, la Data API (REST/GraphQL) ni `supabase-js`, y ninguna clave de Supabase (`anon`,
`service_role`, `sb_secret_…`) aparece en el frontend ni en el repo. Toda la autenticación y el
acceso a datos pasan por FastAPI.

## Conexión
- **Session pooler**, puerto 5432, usuario `postgres.<project-ref>`, host
  `aws-<n>-<región>.pooler.supabase.com`. La conexión directa (`db.<ref>.supabase.co`) es solo IPv6
  en el plan gratuito y Docker en Windows sale por IPv4.
- No usar el Transaction pooler (6543): da problemas con sentencias preparadas.
- Driver psycopg 3: `postgresql+psycopg://…?sslmode=require`, con `pool_pre_ping` y pool pequeño
  (`DB_POOL_SIZE=5`, `DB_MAX_OVERFLOW=5`).
- El código solo depende de `DATABASE_URL`; cambiar de proveedor no requiere cambiar código.

## Endurecimiento (se comprueba en cada auditoría)
| Medida | Dónde | Estado |
|---|---|---|
| Tablas en el esquema `tallerya`, nunca en `public` | migraciones + `search_path` | ✅ `search_path` fijado (Fase 0); tablas desde Fase 1 |
| `ENABLE ROW LEVEL SECURITY` en todas las tablas, sin políticas para `anon`/`authenticated` | migraciones | ⏳ Fase 1 |
| `REVOKE ALL ON SCHEMA tallerya FROM anon, authenticated` | migración inicial | ⏳ Fase 1 |
| Tabla de versiones de Alembic en `tallerya` | `alembic/env.py` | ⏳ Fase 1 |
| Data API desactivada | panel de Supabase | ⏳ acción manual (ver abajo) |
| Security Advisor sin avisos | panel de Supabase | ⏳ auditoría final (Fase 6) |
| Tests nunca contra Supabase | `backend/tests/conftest.py` | ✅ aborta si la URL contiene `supabase.co`/`supabase.com` |

### Acción manual: desactivar la Data API
En el panel del proyecto: **Integrations → Data API** → desactívala. La app no la usa y así ningún
esquema queda expuesto por REST/GraphQL aunque se cambien permisos por error.

## Pausa del plan gratuito
El proyecto se pausa tras una semana sin actividad. `/api/v1/health` devolverá `503`. Reactívalo
desde el [panel](https://supabase.com/dashboard) → proyecto → **Restore project**.
