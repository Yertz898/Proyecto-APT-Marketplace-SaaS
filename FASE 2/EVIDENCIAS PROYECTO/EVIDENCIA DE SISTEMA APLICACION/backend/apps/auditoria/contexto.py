"""
La petición en curso, al alcance de las señales.

Una señal `post_save` no recibe la petición, y sin ella no hay forma de saber
quién hizo el cambio. El middleware la deja en una variable de contexto, que es
segura con hilos y con código asíncrono, y la quita al terminar.

DRF autentica dentro de la vista y deja al usuario en la petición de Django, así
que cuando la señal la lee, el usuario del token ya está puesto.
"""

from contextvars import ContextVar

_peticion: ContextVar = ContextVar("peticion_en_curso", default=None)


class MiddlewareDeAuditoria:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        marca = _peticion.set(request)
        try:
            return self.get_response(request)
        finally:
            _peticion.reset(marca)


def peticion_en_curso():
    return _peticion.get()


def usuario_en_curso():
    peticion = peticion_en_curso()
    usuario = getattr(peticion, "user", None)
    if usuario is not None and usuario.is_authenticated:
        return usuario
    return None


def ip_en_curso():
    peticion = peticion_en_curso()
    if peticion is None:
        return None
    # Detrás del proxy de Railway la IP real viene en la cabecera; el primer
    # valor es el cliente.
    reenviada = peticion.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = reenviada.split(",")[0].strip() or peticion.META.get("REMOTE_ADDR")
    return ip or None
