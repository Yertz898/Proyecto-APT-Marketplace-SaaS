"""Escribir una línea en el registro de actividad."""

import logging

from apps.auditoria.contexto import ip_en_curso, usuario_en_curso
from apps.auditoria.models import Registro

log = logging.getLogger(__name__)


def registrar(accion, modelo, objeto="", *, tienda=None, usuario=None, detalle=None):
    """
    Anota una acción.

    Sin usuario explícito toma el de la petición en curso. Nunca rompe la
    operación que se está registrando: si anotar falla, la acción del usuario
    ya ocurrió y no tiene sentido devolverle un error por eso.
    """
    usuario = usuario or usuario_en_curso()
    try:
        return Registro.objects.create(
            accion=accion,
            modelo=str(modelo)[:80],
            objeto=str(objeto)[:200],
            tienda=tienda,
            tienda_nombre=(getattr(tienda, "nombre", "") or "")[:120],
            usuario=usuario,
            usuario_email=getattr(usuario, "email", "") or "",
            detalle=detalle or {},
            ip=ip_en_curso(),
        )
    except Exception as error:  # noqa: BLE001 — anotar nunca tumba la acción
        log.warning("No se pudo anotar en el registro: %s", type(error).__name__)
        return None
