# Supabase: usage and hardening

**English** · [Español](supabase.es.md)

TallerYA uses Supabase **only as managed PostgreSQL**. Supabase Auth, Storage, Edge Functions, the
Data API (REST/GraphQL) and `supabase-js` are not used, and no Supabase key (`anon`,
`service_role`, `sb_secret_…`) appears in the frontend or in the repo. All authentication and data
access go through FastAPI.

## Connection
- **Session pooler**, port 5432, user `postgres.<project-ref>`, host
  `aws-<n>-<region>.pooler.supabase.com`. The direct connection (`db.<ref>.supabase.co`) is
  IPv6-only on the free plan, and Docker on Windows usually egresses over IPv4.
- Do not use the Transaction pooler (6543): it breaks prepared statements.
- psycopg 3 driver: `postgresql+psycopg://…?sslmode=require`, with `pool_pre_ping` and a small pool
  (`DB_POOL_SIZE=5`, `DB_MAX_OVERFLOW=5`).
- The code only depends on `DATABASE_URL`; switching providers needs no code changes.

## Hardening (checked in every audit)
| Measure | Where | Status |
|---|---|---|
| Tables in the `tallerya` schema, never in `public` | migrations + `search_path` | ✅ `search_path` set (Phase 0); tables from Phase 1 |
| `ENABLE ROW LEVEL SECURITY` on every table, no policies for `anon`/`authenticated` | migrations | ⏳ Phase 1 |
| `REVOKE ALL ON SCHEMA tallerya FROM anon, authenticated` | initial migration | ⏳ Phase 1 |
| Alembic version table in `tallerya` | `alembic/env.py` | ⏳ Phase 1 |
| Data API disabled | Supabase dashboard | ⏳ manual action (see below) |
| Security Advisor without warnings | Supabase dashboard | ⏳ final audit (Phase 6) |
| Tests never hit Supabase | `backend/tests/conftest.py` | ✅ aborts if the URL contains `supabase.co`/`supabase.com` |

### Manual action: disable the Data API
In the project dashboard: **Integrations → Data API** → turn it off. The app does not use it, and
this way no schema is exposed over REST/GraphQL even if permissions are changed by mistake.

## Free plan pausing
The project is paused after one week of inactivity and `/api/v1/health` will return `503`.
Reactivate it from the [dashboard](https://supabase.com/dashboard) → project → **Restore project**.
