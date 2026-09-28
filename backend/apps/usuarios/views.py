"""
Vistas de la API de `usuarios`: sesión y alta de compradores.

Todo lo de acá es la puerta de entrada al sistema, así que las tres vistas
públicas van con control de frecuencia. Sin él, probar contraseñas contra el
inicio de sesión no cuesta nada.
"""

from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.usuarios.serializers import (
    RegistroCompradorSerializer,
    TokenDeSesionSerializer,
    UsuarioSerializer,
)

#: Todas las vistas de sesión comparten el mismo contador de intentos.
AMBITO_AUTENTICACION = "autenticacion"


class IniciarSesion(TokenObtainPairView):
    """Correo y contraseña a cambio de los dos tokens."""

    serializer_class = TokenDeSesionSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = AMBITO_AUTENTICACION


class RenovarSesion(TokenRefreshView):
    """Token de acceso nuevo a partir del de refresco."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = AMBITO_AUTENTICACION


class RegistroComprador(CreateAPIView):
    """
    Alta de un comprador.

    Es la única cuenta que se crea sola. El serializador fija el rol, así que no
    hay forma de registrarse como dueño ni de quedar colgando de una tienda.
    """

    serializer_class = RegistroCompradorSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = AMBITO_AUTENTICACION


class Yo(RetrieveAPIView):
    """
    Quién es el usuario de la sesión.

    Lo usa el frontend al cargar para saber si el token que tiene guardado
    todavía sirve y a quién corresponde.
    """

    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
