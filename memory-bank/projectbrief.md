# Project brief — TallerYA

## Objetivo
Sustituir el Excel con el que el dueño de TallerYA apunta las citas por una web con:
landing informativa, registro/login, reservas con pago simulado y confirmación manual,
y un backoffice (dashboard, calendario, gestión) para el dueño y los profesores.

## Alcance
- Talleres (categorías): Cocina, Cerámica, Música, Pintura, Dibujo, Fotografía.
- Curso = edición concreta de un taller: título, descripción, taller, profesor, inicio, duración,
  coste (EUR, en céntimos), plazas (máx. 10), ubicación, estado
  (borrador, publicado, completo, finalizado, cancelado). Una sola sesión por curso.
- **Todos los cursos son presenciales.**
- Roles: ADMIN (dueño), PROFESOR, ALUMNO.
- Reservas: máquina de estados con caducidad de 24 h y control de plazas concurrente.
- Pago simulado detrás de una interfaz `PaymentProvider`.
- Notificaciones transaccionales y opcionales (con consentimiento); Mailpit en desarrollo.
- Formulario de contacto con honeypot y rate limit; bandeja en backoffice.
- Backoffice: dashboard (pandas + Recharts accesible), calendario, CRUDs, inscripción manual,
  exportar/importar Excel, auditoría. El profesor solo ve lo suyo.
- Complementos (Fase 6): lista de espera, asistencia, páginas legales, cookies, SEO, supresión de cuenta.

## Requisitos no funcionales
- WCAG 2.2 AA, mobile first, `lang="es"`.
- Seguridad: Argon2id, JWT en cookies httpOnly + CSRF, autorización en backend, sin secretos en repo.
- Supabase solo como PostgreSQL (esquema `tallerya`, RLS activado). Tests contra Postgres local.
- Calidad: cobertura ≥ 80 % en `services/` y `api/`, lint, tipos, auditoría por fase.

## Fases
0 Arranque · 1 Datos y auth · 2 Lógica de negocio · 3 Landing · 4 Área de alumno ·
5 Backoffice · 6 Endurecimiento. Detalle en `PROMPT.md` §10.
