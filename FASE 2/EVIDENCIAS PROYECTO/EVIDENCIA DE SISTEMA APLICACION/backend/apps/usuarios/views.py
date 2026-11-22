"""
Vistas de la API de `usuarios`: sesión y alta de compradores.

Todo lo de acá es la puerta de entrada al sistema, así que las tres vistas
públicas van con control de frecuencia. Sin él, probar contraseñas contra el
inicio de sesión no cuesta nada.
"""

from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.auditoria.models import Accion
from apps.auditoria.registrar import registrar
from apps.usuarios.cuenta import CambiosDeCuentaSerializer
from apps.usuarios.models import Rol, Usuario
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

    def post(self, request, *args, **kwargs):
        respuesta = super().post(request, *args, **kwargs)
        # Solo se anotan los inicios de sesión de quienes administran algo: los
        # compradores entran a muchas tiendas y su sesión no es un cambio en
        # ninguna.
        # Con la verificación en dos pasos, este paso todavía no inicia la
        # sesión: se anota cuando se valida el código.
        if respuesta.status_code == 200 and "access" in respuesta.data:
            usuario = Usuario.objects.filter(
                email__iexact=request.data.get("email", "")
            ).first()
            if usuario and usuario.rol != Rol.COMPRADOR:
                registrar(
                    Accion.SESION,
                    "sesión",
                    usuario.email,
                    tienda=usuario.tienda,
                    usuario=usuario,
                )
        return respuesta


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


class Yo(RetrieveUpdateAPIView):
    """
    Quién es el usuario de la sesión, y el cambio de su nombre.

    Lo usa el frontend al cargar para saber si el token que tiene guardado
    todavía sirve y a quién corresponde. Con PATCH se edita el nombre, que es
    lo único de la cuenta propia que no pide más verificación.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return CambiosDeCuentaSerializer
        return UsuarioSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(UsuarioSerializer(request.user).data)
