"""
Formato único de error de la API.

Una respuesta de error siempre tiene la misma forma
(CONVENCIONES.md > Errores y respuestas de la API):

    {"error": {"codigo": "...", "mensaje": "...", "detalles": {...}}}

`mensaje` es para mostrarle a la persona, en español. `codigo` es para que el
frontend decida qué hacer sin leer el texto.

Un error nunca filtra detalles internos. Lo que no es una excepción de DRF ni
siquiera pasa por acá: lo maneja Django, que con DEBUG apagado responde sin
trazas ni consultas.
"""

from django.core.exceptions import PermissionDenied as PermisoDenegadoDeDjango
from django.http import Http404
from rest_framework import exceptions
from rest_framework.views import exception_handler

#: Código y mensaje por tipo de excepción. El mensaje es el que se muestra
#: cuando la vista no escribió uno propio.
POR_EXCEPCION = {
    exceptions.ValidationError: ("validacion", "Revisa los datos marcados."),
    exceptions.NotAuthenticated: ("sin_sesion", "Inicia sesión para continuar."),
    exceptions.AuthenticationFailed: (
        "credenciales_invalidas",
        "El correo o la contraseña no coinciden.",
    ),
    exceptions.PermissionDenied: (
        "sin_permiso",
        "Tu cuenta no puede hacer esto.",
    ),
    # El mensaje es a propósito el mismo para «no existe» y «no es tuyo»: un
    # texto distinto confirmaría que el recurso existe en otra tienda.
    exceptions.NotFound: ("no_encontrado", "No encontramos lo que buscas."),
    exceptions.MethodNotAllowed: (
        "metodo_no_permitido",
        "Esa acción no está disponible acá.",
    ),
    exceptions.Throttled: (
        "demasiados_intentos",
        "Demasiados intentos seguidos. Espera un momento y vuelve a probar.",
    ),
}

GENERICO = ("error", "No pudimos completar la operación.")

#: Excepciones cuyo mensaje es siempre el nuestro, aunque la vista o una
#: librería hayan escrito otro. Un fallo de sesión tiene una sola cosa que
#: decir, y decir de más es contar quién tiene cuenta y quién no.
MENSAJE_SIEMPRE_NUESTRO = (exceptions.AuthenticationFailed, exceptions.Throttled)


def _codigo_y_mensaje(exc):
    """Busca el tipo exacto y, si no está, sube por la jerarquía."""
    for tipo in type(exc).__mro__:
        if tipo in POR_EXCEPCION:
            return POR_EXCEPCION[tipo]
    return GENERICO


def _mensaje_de_la_vista(exc, por_omision):
    """
    El texto que escribió la vista, si escribió uno.

    Los mensajes por omisión de DRF vienen en inglés y no se le muestran a
    nadie; los que escribe una vista sí, y suelen decir algo más útil.
    """
    detalle = exc.detail
    if isinstance(detalle, dict | list):
        return por_omision

    texto = str(detalle)
    return por_omision if texto == str(exc.default_detail) else texto


def _como_lista(valor):
    """
    Cada campo termina siendo una lista de textos, siempre.

    DRF devuelve a veces un texto suelto, a veces una lista y a veces un
    diccionario anidado. Normalizarlo acá le ahorra al formulario tener que
    adivinar la forma en cada campo.
    """
    if isinstance(valor, list):
        return [texto for item in valor for texto in _como_lista(item)]
    if isinstance(valor, dict):
        return [texto for item in valor.values() for texto in _como_lista(item)]
    return [str(valor)]


def _detalles(exc):
    """Los errores campo por campo, para que el formulario los ubique."""
    if isinstance(exc, exceptions.ValidationError):
        detalle = exc.detail
        if not isinstance(detalle, dict):
            detalle = {"general": detalle}
        return {campo: _como_lista(valor) for campo, valor in detalle.items()}

    if isinstance(exc, exceptions.Throttled) and exc.wait:
        return {"segundos": int(exc.wait)}

    return {}


def manejador_de_errores(exc, context):
    respuesta = exception_handler(exc, context)
    if respuesta is None:
        return None

    # DRF traduce por dentro las excepciones de Django a las suyas para armar la
    # respuesta, pero a este manejador le llega la original. `get_object_or_404`
    # levanta la de Django, así que sin esto un 404 caería en el caso genérico.
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermisoDenegadoDeDjango):
        exc = exceptions.PermissionDenied()

    codigo, mensaje = _codigo_y_mensaje(exc)

    if not isinstance(exc, MENSAJE_SIEMPRE_NUESTRO):
        mensaje = _mensaje_de_la_vista(exc, mensaje)

    respuesta.data = {
        "error": {"codigo": codigo, "mensaje": mensaje, "detalles": _detalles(exc)}
    }
    return respuesta
