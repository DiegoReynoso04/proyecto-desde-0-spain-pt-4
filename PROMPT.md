0. Rol y forma de trabajar

Actúa como un equipo full‑stack senior (arquitecto, backend Python, frontend React/Next, QA y especialista en accesibilidad). Vas a construir TallerYA, una web con landing informativa, área de alumnos con reservas y un backoffice para el dueño y los profesores.

Reglas generales:

Trabaja por fases (sección 10). No empieces una fase sin haber cerrado la anterior.
Antes de la Fase 1, lee la sección 11 («Supuestos y dudas»), y pregúntame lo que no esté claro. No inventes requisitos de negocio: si algo es ambiguo, pregunta o documenta el supuesto en memory-bank/decisions.md.
Cada fase termina con: tests en verde → debugging → auditoría → commit(s) → Pull Request → actualizar memory-bank/ → parar y darme un resumen. No hagas merge ni empieces la siguiente fase hasta que yo lo apruebe.
Distingue siempre en tus informes entre lo verificado (tests ejecutados, comandos con salida) y lo supuesto.
Trabajo en Windows con Docker Desktop (WSL2). Ten en cuenta finales de línea (.gitattributes), rutas y hot‑reload en contenedores.
1. Contexto de negocio

El dueño de TallerYA ofrece talleres presenciales de cocina, cerámica, música, pintura, dibujo y fotografía. Hoy apunta las citas en un Excel. Quiere:

Una landing únicamente informativa (qué es TallerYA, talleres, profesores, ubicación, preguntas frecuentes, contacto).
Que la gente pueda registrarse, iniciar sesión y reservar cursos.
Una simulación de pago y un flujo de confirmación manual.
Un backoffice con dashboard, calendario y gestión.

Todos los cursos son presenciales. Debe aparecer claramente en la landing, en la ficha de cada curso y en los correos.

Conceptos
Taller: categoría (Cocina, Cerámica, Música, Pintura, Dibujo, Fotografía).
Curso: una edición concreta de un taller, con: título, descripción, taller, profesor asignado, fecha y hora de inicio, duración, coste (EUR), plazas máximas = 10 (valor por defecto y máximo), ubicación (aula/dirección), estado (borrador, publicado, completo, finalizado, cancelado).
2. Requisitos funcionales
2.1 Usuarios y autenticación

Roles: ADMIN (dueño), PROFESOR, ALUMNO.

Alumno: se registra en la web pública con nombre, teléfono, correo electrónico y contraseña.
Validaciones: email válido y único; teléfono en formato español/internacional (E.164, usa phonenumbers); contraseña mínima de 10 caracteres, con indicador de fortaleza.
Casilla obligatoria de aceptación de la política de privacidad (RGPD).
Casilla opcional de consentimiento de notificaciones (recordatorios y novedades). Desmarcada por defecto. Se guarda la fecha y versión del texto aceptado.
Profesor y Admin: acceden al backoffice por un login separado (/backoffice/login). El admin crea las cuentas de profesor.
Contraseñas cifradas con hash (Argon2id con pwdlib[argon2] o argon2-cffi) para todos los roles. Nunca en texto plano, nunca en logs.
Sesión con JWT de acceso corto + refresh token, en cookies httpOnly, Secure, SameSite=Lax. Protección CSRF para peticiones que modifican datos.
Recuperación de contraseña por email con token de un solo uso y caducidad.
Límite de intentos de login (rate limiting) y bloqueo temporal.
Nadie puede reservar sin estar registrado y con sesión iniciada. La landing solo informa; el botón «Reservar» lleva a login/registro y, tras iniciar sesión, vuelve al curso.
2.2 Reservas (máquina de estados)
PENDIENTE_PAGO ──(pago simulado OK)──▶ PAGADA ──(admin inscribe en backoffice)──▶ CONFIRMADA
      │                                   │
      ├──(24 h sin pago)──▶ EXPIRADA      └──(admin cancela/reembolsa)──▶ CANCELADA
      └──(alumno cancela)──▶ CANCELADA

Reglas:

Al reservar se crea la reserva en PENDIENTE_PAGO con expires_at = min(created_at + 24 h, inicio_del_curso). Es una reserva, no una inscripción confirmada.
Una reserva en PENDIENTE_PAGO, PAGADA o CONFIRMADA ocupa plaza. Máximo 10 plazas activas por curso.
Una persona no puede tener más de una reserva activa en el mismo curso, pero sí en cursos distintos. Implementar con un índice único parcial en PostgreSQL (UNIQUE (user_id, course_id) WHERE status IN ('PENDIENTE_PAGO','PAGADA','CONFIRMADA')) además de la validación en servicio.
Concurrencia: el control de plazas debe ser seguro ante dos reservas simultáneas (transacción + SELECT ... FOR UPDATE sobre el curso). Escribe un test que lo demuestre.
Expiración: un proceso programado (servicio scheduler en Docker, cada 5 minutos) pasa a EXPIRADA las reservas vencidas y libera la plaza. Además, la comprobación también se hace al leer (expiración perezosa) para no depender solo del job.
No se puede reservar un curso pasado, cancelado o completo.
El alumno ve en «Mis reservas» el estado y una cuenta atrás hasta la expiración, y puede pagar o cancelar.
2.3 Pago simulado
Página de checkout ficticia y claramente marcada como simulación («Entorno de pruebas — no se realiza ningún cargo»).
Botones/acciones para simular pago correcto y pago rechazado (o tarjetas de prueba tipo 4242 4242 4242 4242 = OK, 4000 0000 0000 0002 = rechazada).
No guardar números de tarjeta ni CVV, ni siquiera de prueba. Solo: referencia del pago, importe, estado, fecha y, como mucho, los 4 últimos dígitos.
Al confirmarse el pago: la reserva pasa a PAGADA y se notifica al dueño (notificación en el backoffice + email). El dueño inscribe manualmente al alumno desde el backoffice → CONFIRMADA, y el alumno recibe un email de confirmación.
Diseña el módulo de pago detrás de una interfaz (PaymentProvider) para poder cambiar en el futuro a Stripe/Redsys sin tocar la lógica de reservas.
2.4 Notificaciones
Transaccionales (siempre, no requieren consentimiento): registro, reserva creada, aviso de expiración próxima, reserva expirada, pago recibido, inscripción confirmada, recuperación de contraseña.
Opcionales (solo con consentimiento): recordatorio 24 h antes del curso, novedades.
Al dueño: pago recibido, nuevo mensaje de contacto.
En desarrollo, los emails se capturan con Mailpit (contenedor Docker); nunca se envían de verdad.
2.5 Formulario de contacto (landing)
Campos: nombre, email, teléfono (opcional), taller de interés (select), mensaje, casilla de privacidad obligatoria.
Validación en cliente (mensajes accesibles, asociados al campo con aria-describedby) y en servidor (Pydantic).
Antispam: campo honeypot + rate limiting por IP.
Los mensajes se guardan en BD y aparecen en una bandeja del backoffice (leído/respondido).
2.6 Backoffice

Admin (dueño):

Dashboard: ingresos (mes, por taller), ocupación por curso (%), reservas pendientes de pago y pagadas pendientes de inscribir, próximos cursos, tasa de expiración, nuevos alumnos. Cálculos con pandas en el backend; gráficos accesibles en el frontend (Recharts), con tabla alternativa para lectores de pantalla.
Calendario (mes/semana/día) con los cursos y, al abrir un curso, la lista de personas y su estado. Navegable con teclado.
Gestión: CRUD de talleres, cursos y profesores; listado y filtros de reservas; acción «Inscribir» sobre las PAGADA; cancelar reservas.
Alumnos: listado, ficha, historial de reservas.
Bandeja de contacto.
Notificaciones (campana con contador).
Exportar a CSV/Excel (reservas, alumnos por curso) e importar el Excel actual del dueño con pandas (validar columnas, informe de filas erróneas, modo «previsualizar antes de guardar»).
Registro de auditoría (quién inscribió, canceló o editó qué y cuándo).

Profesor:

Solo ve sus cursos asignados y sus alumnos (los de sus cursos), su calendario y la lista de asistentes. No ve ingresos globales ni datos de otros profesores. La autorización se aplica en el backend, no solo ocultando botones.
2.7 Complementos que añado (implementar si da tiempo, en la Fase 6)
Lista de espera cuando un curso está completo (aviso al liberarse plaza).
Marcar asistencia por parte del profesor.
Páginas legales: aviso legal, privacidad, cookies y declaración de accesibilidad.
Banner de cookies (solo cookies técnicas si no hay analítica).
SEO básico: metadatos, Open Graph, sitemap.xml, robots.txt, datos estructurados Course/LocalBusiness.
Derecho de supresión: el alumno puede eliminar su cuenta (anonimizando reservas históricas).
3. Stack técnico
Capa	Tecnología
Frontend	Next.js (versión estable actual, App Router) + React + TypeScript sobre Node LTS
Estilos	Tailwind CSS (si es v4, tokens en @theme)
Formularios	React Hook Form + Zod (validación cliente)
Backend	Python 3.12+, FastAPI, API REST versionada (/api/v1)
Validación	Pydantic v2 (+ pydantic-settings para configuración)
ORM / migraciones	SQLAlchemy 2.x + Alembic
Datos	pandas para dashboard, exportación e importación
BD	Supabase (PostgreSQL) para la app · PostgreSQL 17 local en Docker para tests
Emails dev	Mailpit
Tests	pytest, httpx, pytest-cov · Vitest + Testing Library · Playwright + @axe-core/playwright
Calidad	ruff, mypy, ESLint, tsc --noEmit, Prettier, pre-commit
Seguridad	pip-audit, npm audit, bandit

El frontend llama al backend a través de un rewrite de Next (/api/* → FastAPI) para que las cookies sean del mismo origen.

Base de datos: Supabase (PostgreSQL gestionado)
Proyecto Supabase: https://hfhjwuvpxdfeidvjedai.supabase.co (project ref hfhjwuvpxdfeidvjedai).
Supabase se usa solo como PostgreSQL. No se usan Supabase Auth, Storage, Edge Functions ni la Data API (REST/GraphQL) ni supabase-js. Toda la autenticación y el acceso a datos pasan por FastAPI.
Conexión: el backend corre en Docker sobre Windows, que normalmente sale por IPv4, y la conexión directa de Supabase (db.<ref>.supabase.co) es IPv6 en el plan gratuito. Por eso se usa el Session pooler (puerto 5432, usuario postgres.hfhjwuvpxdfeidvjedai, host aws-<n>-<region>.pooler.supabase.com). No uses el Transaction pooler (6543), que da problemas con sentencias preparadas.
Driver: psycopg 3 (postgresql+psycopg://...?sslmode=require), el mismo para la app y para Alembic. pool_pre_ping=True y pool pequeño (DB_POOL_SIZE=5, DB_MAX_OVERFLOW=5) por los límites de conexiones del plan gratuito.
Esquema propio: todas las tablas van en el esquema tallerya (no en public), con search_path=tallerya y la tabla de versiones de Alembic también en ese esquema. Así nunca quedan expuestas por la Data API.
Tests: nunca contra Supabase. Los tests usan el PostgreSQL 17 local del contenedor db (TEST_DATABASE_URL). El conftest.py debe abortar si la URL de test contiene supabase.com o supabase.co.
Seed: scripts/seed.py exige el flag --confirm-remote para escribir en Supabase y nunca borra datos existentes sin un segundo flag explícito (--reset).
El plan gratuito pausa el proyecto tras una semana sin actividad; documéntalo en el README (cómo reactivarlo desde el panel).
El código solo depende de DATABASE_URL: si en el futuro se cambia de proveedor, no hay que tocar código.
4. Diseño, paleta y accesibilidad
Paleta (tokens de Tailwind)
Token	Hex	Uso
ocre-400
#D99F59	Fondos de botones primarios, acentos, decoraciones
ocre-300
#D99962	Hover / fondos suaves de acento
terracota-500
#A67153	Bordes, iconos, texto grande (≥ 24 px o ≥ 18,66 px en negrita)
cacao-700
#733F2D	Texto principal, enlaces, encabezados, foco
crema-50
#F2F2F2	Fondo general
tinta-900
#1F1F1F	Texto sobre fondos ocre (añadido por accesibilidad)

Contrastes ya calculados (fórmula WCAG 2.x), respétalos:

#733F2D sobre
#F2F2F2 → 7,57:1 ✅ texto normal (AA y AAA).
#1F1F1F sobre
#D99F59 → 7,11:1 ✅ → los botones ocre llevan texto oscuro.
Blanco sobre
#D99F59 → 2,32:1 ❌ prohibido para texto.
#D99F59 sobre
#F2F2F2 → 2,07:1 ❌ nunca como color de texto ni como único borde de un control.
#A67153 sobre
#F2F2F2 → 3,67:1 ⚠️ solo texto grande, iconos y bordes de componentes (≥ 3:1), nunca texto de párrafo.

Crea un test automático (script o test unitario) que compruebe los pares texto/fondo de los tokens y falle si alguno baja de 4,5:1 (texto normal) o 3:1 (texto grande / componentes).

Accesibilidad: WCAG 2.2 nivel AA
HTML semántico, landmarks (header, nav, main, footer), un solo h1 por página, jerarquía de encabezados correcta.
Enlace «Saltar al contenido», navegación completa por teclado, foco visible (anillo cacao-700 de 2 px con offset), sin trampas de foco; modales con foco gestionado.
Formularios con label visible, errores en texto (no solo color), aria-invalid, aria-describedby y resumen de errores al enviar.
Objetivos táctiles de al menos 24×24 px (mejor 44×44 en móvil).
alt descriptivos en español; imágenes decorativas con alt="".
Respetar prefers-reduced-motion.
La cuenta atrás de la reserva no debe anunciarse cada segundo (usa aria-live="polite" con actualizaciones espaciadas).
Idioma lang="es".
Auditoría con axe (Playwright) en todas las páginas y Lighthouse Accesibilidad ≥ 95, más revisión manual con teclado.
Mobile First

Diseña primero para 360 px y amplía con breakpoints sm, md, lg. El backoffice también debe funcionar en móvil (tablas que pasan a tarjetas, calendario en vista lista/día).

Imágenes y contenido
Imágenes de bancos gratuitos (Unsplash o Pexels). Estética coherente: luz natural, tonos cálidos (ocres, terracota, madera, barro), manos trabajando, ambiente de taller. Una imagen principal por taller + hero + sección «sobre nosotros».
Descárgalas a frontend/public/images/, conviértelas a WebP/AVIF y sírvelas con next/image (tamaños responsive, priority solo en el hero).
Registra autor, URL de origen y licencia de cada imagen en docs/CREDITS.md.
Textos: redacta contenido original para TallerYA (no copies textos de otras webs). Tono cercano y claro.
5. Seguridad
Hash Argon2id para contraseñas; nunca devolver el hash en respuestas.
Autorización por rol y por propiedad del recurso en cada endpoint (un alumno solo ve sus reservas; un profesor solo sus cursos).
CORS restringido, cabeceras de seguridad (CSP, HSTS en prod, X-Content-Type-Options, Referrer-Policy).
Secretos solo en .env (ya existe en la raíz del proyecto; no lo regeneres ni lo sobrescribas). Se commitea .env.example sin valores reales; .env va en .gitignore desde el primer commit. Antes de cada commit, comprueba con git status que .env no está en el staging.
Configuración leída con pydantic-settings; la app debe fallar al arrancar si falta una variable obligatoria o si un secreto tiene menos de 32 caracteres.
Endurecimiento de Supabase (documentar en docs/ y comprobar en la auditoría):
Tablas en el esquema tallerya, nunca en public.
ENABLE ROW LEVEL SECURITY en todas las tablas desde las migraciones (sin políticas para anon/authenticated), como defensa adicional.
REVOKE ALL ON SCHEMA tallerya FROM anon, authenticated; en la migración inicial.
Indicarme que desactive la Data API en el panel (Integrations → Data API) porque no se usa, y revisar el Security Advisor del panel en la auditoría final.
Ninguna clave de Supabase (anon, service_role, sb_secret_...) en el frontend ni en el repo. Esta app no las necesita.
Validación de toda entrada con Pydantic; consultas parametrizadas (ORM).
Logs sin datos personales sensibles ni tokens.
Fechas en UTC en la BD; mostrar en Europe/Madrid.
Importes en céntimos (entero) para evitar errores de redondeo.
6. Estructura del repositorio
tallerya/
├─ CLAUDE.md
├─ README.md / README.es.md
├─ docker-compose.yml
├─ docker-compose.override.yml      # dev: hot reload
├─ .env.example
├─ .gitattributes / .gitignore / .pre-commit-config.yaml
├─ .github/workflows/ci.yml
├─ memory-bank/
├─ docs/  (arquitectura, API, accesibilidad, auditorías, CREDITS.md)
├─ backend/
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  ├─ alembic/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ core/        (config, seguridad, db)
│  │  ├─ models/      (SQLAlchemy)
│  │  ├─ schemas/     (Pydantic)
│  │  ├─ repositories/
│  │  ├─ services/    (reservas, pagos, notificaciones, analytics con pandas)
│  │  ├─ api/v1/      (routers)
│  │  └─ jobs/        (expiración de reservas, recordatorios)
│  ├─ scripts/seed.py
│  └─ tests/ (unit, integration)
└─ frontend/
   ├─ Dockerfile
   ├─ app/
   │  ├─ (public)/      landing, talleres, cursos, contacto, legales
   │  ├─ (auth)/        login, registro, recuperar contraseña
   │  ├─ (alumno)/      mis reservas, checkout simulado, perfil
   │  └─ backoffice/    login, dashboard, calendario, cursos, reservas, alumnos, profesores, mensajes
   ├─ components/ (ui accesibles reutilizables)
   ├─ lib/ (cliente API, validaciones Zod)
   ├─ public/images/
   └─ tests/ (unit + e2e)
7. Docker

docker-compose.yml con estos servicios:

db: postgres:17-alpine, volumen nombrado, healthcheck con pg_isready. Solo para tests (y para trabajar sin conexión si hace falta); la app usa Supabase. Credenciales desde POSTGRES_* del .env.
backend: FastAPI con uvicorn, conectado a Supabase vía DATABASE_URL. Las migraciones se ejecutan con un comando explícito (alembic upgrade head), no automáticamente al arrancar, para no tocar la BD remota sin querer.
Todos los servicios leen el .env de la raíz con env_file: .env. Las variables NEXT_PUBLIC_* se pasan como build args al frontend, porque se fijan en el build.
scheduler: misma imagen que el backend, ejecuta los jobs (expiración cada 5 min, recordatorios).
frontend: Next.js (en dev con hot reload y WATCHPACK_POLLING=true por Windows; en prod next build + next start con build multi‑stage).
mailpit: SMTP de pruebas con interfaz web.
(Opcional) adminer para inspeccionar la BD en dev.

Requisitos: docker compose up --build debe levantar todo desde cero; make seed (o un script equivalente que funcione en Windows) crea datos de ejemplo: 1 admin, 3 profesores, los 6 talleres, ~12 cursos en las próximas semanas, alumnos y reservas en todos los estados. Imágenes con usuario no root.

8. Tests, debugging y auditorías

Tests mínimos obligatorios:

Todos los tests usan TEST_DATABASE_URL (Postgres local). Ningún test se conecta a Supabase.
Backend (pytest, cobertura ≥ 80 % en services/ y api/):
Registro/login/refresh/logout, hash de contraseñas, rate limit.
Reserva duplicada en el mismo curso → rechazada; en otro curso → permitida.
Plaza 11 → rechazada; dos reservas concurrentes por la última plaza → solo una gana.
Expiración a las 24 h (con reloj simulado, p. ej. freezegun o time-machine) libera la plaza.
Pago simulado OK/KO; notificación al dueño; inscripción manual; transiciones de estado inválidas → error.
Permisos: profesor no ve cursos ajenos; alumno no ve reservas ajenas.
Contacto: validaciones y honeypot.
Dashboard: agregados de pandas con datos conocidos.
Frontend (Vitest + Testing Library): formularios y sus errores, componentes accesibles.
E2E (Playwright): registro → reserva → pago simulado → admin inscribe → alumno ve «Confirmada»; y análisis axe en cada página.

Al final de cada fase, auditoría documentada en docs/auditorias/fase-N.md:

Lint y tipos: ruff, mypy, eslint, tsc --noEmit.
Tests y cobertura.
Seguridad: pip-audit, npm audit, bandit, revisión de endpoints y permisos.
Accesibilidad (fases con UI): axe + Lighthouse + revisión con teclado.
Rendimiento básico (fases con UI): Lighthouse móvil.
Lista de problemas encontrados, cuáles se corrigieron y cuáles quedan pendientes.

Debugging: cuando un test falle, reproduce, identifica la causa raíz, corrige y añade un test de regresión. Anota en memory-bank/progress.md los bugs relevantes.

9. Control de versiones (Git + GitHub)
Inicializa el repo, rama principal main. Si no existe el repo remoto, pregúntame el nombre y créalo con gh.
Una rama por fase: feat/fase-N-descripcion.
Commits pequeños con Conventional Commits (feat:, fix:, test:, docs:, chore:, refactor:).
Al cerrar la fase: push y Pull Request con gh pr create, con descripción: qué se hizo, cómo probarlo, resultado de la auditoría y pendientes.
CI en GitHub Actions (.github/workflows/ci.yml): lint, tipos, tests backend con servicio PostgreSQL, tests frontend y build. El PR solo se considera listo con la CI en verde.
No hagas merge sin mi aprobación.
10. Fases de desarrollo
Fase	Contenido	Entregable
0. Arranque	Repo, .gitignore con .env (lo primero), .gitattributes, CLAUDE.md, memory-bank/, README.md + README.es.md, Docker Compose con db + mailpit + esqueletos de backend y frontend que arrancan, CI (con un PostgreSQL de servicio, nunca Supabase), pre-commit (incluye detección de secretos, p. ej. detect-secrets o gitleaks)	docker compose up levanta todo y /api/v1/health devuelve el estado de la conexión a Supabase (SELECT 1)
1. Datos y autenticación	Modelos, migraciones Alembic, roles, registro/login alumnos, login backoffice, hash, cookies, CSRF, rate limit, recuperación de contraseña, seed	Auth completa con tests
2. Lógica de negocio	Talleres, cursos, reservas (estados, plazas, duplicados, concurrencia), pago simulado, scheduler de expiración, notificaciones y emails, contacto	API documentada en /docs (OpenAPI) con tests
3. Landing	Diseño mobile first, tokens de color, landing informativa (presencial bien visible), talleres, cursos (solo lectura), profesores, FAQ, contacto, imágenes con créditos, páginas legales	Landing accesible con axe sin errores
4. Área de alumno	Registro/login UI, reservar, checkout simulado, «Mis reservas» con cuenta atrás, perfil, consentimientos	Flujo E2E alumno
5. Backoffice	Dashboard con pandas, calendario, CRUDs, inscripción manual, notificaciones, bandeja de contacto, vista de profesor, exportar/importar Excel, auditoría	Flujo E2E admin y profesor
6. Endurecimiento	Complementos de 2.7, auditoría final completa (seguridad, accesibilidad, rendimiento), documentación final	Informe final y guía de despliegue
11. Supuestos y dudas (confírmalos conmigo antes de la Fase 1)
Consentimiento: entiendo que la casilla de notificaciones es opcional y que lo obligatorio es aceptar la política de privacidad. Los correos transaccionales (reserva, pago, confirmación) se envían siempre.
Duplicados: si una reserva caduca o se cancela, la persona puede volver a reservar ese curso. Lo que no puede es tener dos reservas activas del mismo curso.
Plazas: las reservas pendientes de pago ocupan plaza durante sus 24 h.
Duración: cada curso es una única sesión con fecha/hora de inicio y duración en horas. Si el dueño necesita cursos de varias sesiones, se modela una tabla course_sessions.
Límite de 10: es el máximo para todos los cursos; el admin puede bajarlo pero no subirlo.
Cancelación tras el pago: solo la puede hacer el admin (reembolso simulado).
12. CLAUDE.md (créalo en la Fase 0)

Debe ser breve (menos de ~150 líneas) y contener:

Descripción del proyecto en 3 líneas y enlace a memory-bank/.
Instrucción: al empezar cada sesión, lee memory-bank/activeContext.md y memory-bank/progress.md; al terminar una tarea, actualízalos.
Comandos exactos: levantar Docker, migrar, seed, tests backend/frontend/E2E, lint, auditoría.
Convenciones: estructura de carpetas, nombres, Conventional Commits, ramas por fase, PR obligatorio, nada de merge sin aprobación.
Reglas de negocio críticas (estados de reserva, 24 h, 10 plazas, sin duplicados, solo registrados reservan, cursos presenciales).
Reglas de accesibilidad y paleta (incluida la tabla de contrastes permitidos).
Reglas de seguridad (hash, no secretos en el repo, no datos de tarjeta, autorización en backend).
Reglas de base de datos: Supabase solo como PostgreSQL, esquema tallerya, RLS activado, Session pooler, tests siempre contra el Postgres local, seed remoto solo con --confirm-remote, no sobrescribir .env.
«Definición de terminado» de una tarea: tests, lint, tipos, accesibilidad si hay UI, docs y memory-bank actualizados.
Qué no hacer: no añadir dependencias sin justificarlas, no desactivar tests, no saltarse fases, no usar any en TypeScript sin motivo.
13. memory-bank/ (créalo en la Fase 0)
memory-bank/
├─ projectbrief.md     # objetivo, alcance, requisitos (resumen de este prompt)
├─ productContext.md   # usuarios, problemas que resuelve, flujos principales
├─ systemPatterns.md   # arquitectura, máquina de estados, patrones (repositorios, servicios, PaymentProvider)
├─ techContext.md      # stack, versiones, Docker, variables de entorno, comandos
├─ activeContext.md    # fase actual, en qué se está trabajando, próximos pasos
├─ progress.md         # qué está hecho, qué falta, bugs conocidos
└─ decisions.md        # registro de decisiones (ADR breves): fecha, decisión, motivo, alternativas

Mantenlo actualizado al final de cada fase y siempre que tomes una decisión de arquitectura.

14. Documentación
README.md (inglés) y README.es.md (español), con el mismo contenido: qué es, requisitos, cómo arrancar con Docker, cómo ejecutar tests, credenciales de seed, estructura.
Cualquier otro documento para personas en docs/ también en las dos versiones (*.md y *.es.md). El memory-bank/ y CLAUDE.md solo en español (son de uso interno del agente).

Empieza ahora por la sección 11: hazme las preguntas que necesites. Después ejecuta la Fase 0 y para cuando abras el PR.
