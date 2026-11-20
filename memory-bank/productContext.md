# Product context

## Usuarios
- **Visitante**: quiere saber qué es TallerYA, qué talleres hay, cuándo, dónde y cuánto cuesta.
  Solo puede informarse y escribir por el formulario de contacto.
- **Alumno**: se registra (nombre, teléfono E.164, email, contraseña ≥ 10, privacidad obligatoria,
  notificaciones opcionales desmarcadas), reserva, paga (simulado), ve sus reservas y su cuenta atrás.
- **Profesor**: ve solo sus cursos, su calendario y los asistentes de sus cursos.
- **Admin (dueño)**: gestiona todo, inscribe manualmente las reservas pagadas, ve ingresos y métricas.

## Problemas que resuelve
- Citas en un Excel: errores, sin control de plazas, sin historial.
- Reservas "fantasma": la caducidad de 24 h libera plazas automáticamente.
- Falta de visibilidad: dashboard de ingresos, ocupación y pendientes.

## Flujos principales
1. **Reserva**: curso → «Reservar» → login/registro → vuelve al curso → reserva `PENDIENTE_PAGO`
   (24 h o hasta el inicio del curso) → checkout simulado → `PAGADA` → aviso al dueño
   (campana + email) → admin «Inscribir» → `CONFIRMADA` → email al alumno.
2. **Caducidad**: sin pago en plazo → `EXPIRADA` (job cada 5 min + comprobación al leer).
3. **Cancelación**: el alumno cancela su `PENDIENTE_PAGO`; tras el pago solo cancela el admin,
   eligiendo si hay reembolso simulado.
4. **Contacto**: formulario → BD → bandeja del backoffice (leído/respondido) + email al dueño.
5. **Importación**: el dueño sube su Excel actual → previsualización con errores por fila → guardar.
