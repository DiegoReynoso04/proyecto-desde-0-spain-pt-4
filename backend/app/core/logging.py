"""Configuración de logs.

Regla del proyecto: nunca registrar contraseñas, tokens, cadenas de conexión
ni datos personales sensibles. Ante errores de BD se registra solo el tipo.
"""

import logging

_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format=_FORMAT, force=True)
    # El log de acceso de uvicorn no incluye cuerpos ni cabeceras; se mantiene.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
