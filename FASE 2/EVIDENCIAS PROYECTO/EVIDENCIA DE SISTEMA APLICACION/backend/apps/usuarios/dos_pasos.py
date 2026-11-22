"""
Verificación en dos pasos con una app de autenticación (Google Authenticator).

Es **opcional** y solo para las cuentas que administran algo: el dueño de una
tienda y la administración de DealCommerce. Un comprador no la necesita: su
cuenta solo ve sus propios pedidos, y un paso más al comprar espanta ventas.

Cómo funciona:

1. **Activar.** Desde «Tu cuenta», `otp/iniciar` genera un secreto y devuelve
   el QR para escanearlo. Todavía no se pide nada al entrar: falta probar que
   el teléfono quedó bien configurado.
2. **Confirmar.** `otp/confirmar` recibe el primer código de la app. Si es
   válido, la verificación queda activa y se entregan 8 códigos de respaldo
   de un solo uso, por si se pierde el teléfono. Se muestran esa única vez.
3. **Entrar.** Con la verificación activa, el inicio de sesión con correo y
   contraseña ya no entrega los tokens: devuelve un *desafío* firmado que vale
   cinco minutos. `auth/sesion/otp` recibe el desafío y el código (o uno de
   respaldo) y recién ahí entrega los tokens.
4. **Desactivar.** Pide la contraseña y un código: con la sesión abierta en un
   computador prestado no alcanza para apagarla.

Los códigos de la app se aceptan con un paso de tolerancia (±30 segundos) y no
se aceptan dos veces seguidas, para que uno visto por encima del hombro no
sirva para entrar de nuevo. Después de cinco códigos malos se espera.
"""

import base64
import hashlib
import hmac
import io
import secrets

import pyotp
import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.core import signing
from django.core.cache import cache
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings as ajustes_jwt

from apps.auditoria.models import Accion
from apps.auditoria.registrar import registrar
from apps.usuarios.models import Rol, Usuario

#: Quiénes pueden activarla.
ROLES_CON_DOS_PASOS = (Rol.DUENO_TIENDA, Rol.ADMIN_PLATAFORMA)

#: Cuánto vale el desafío entre la contraseña y el código.
VIGENCIA_DEL_DESAFIO = 5 * 60
SAL_DEL_DESAFIO = "usuarios.dos-pasos"

#: Códigos malos tolerados por cuenta antes de hacer esperar.
MAXIMO_DE_FALLOS = 5
ESPERA_TRAS_FALLOS = 5 * 60

CANTIDAD_DE_RESPALDO = 8
EMISOR = "DealCommerce"


def aplica(usuario: Usuario) -> bool:
    return usuario.rol in ROLES_CON_DOS_PASOS


def pide_codigo(usuario: Usuario) -> bool:
    return aplica(usuario) and usuario.otp_activo and bool(usuario.otp_secreto)


# ── Tokens y desafío ────────────────────────────────────────────────────────


def tokens_para(usuario: Usuario) -> dict:
    """Los dos tokens de una sesión, como los entrega el inicio de sesión."""
    from apps.usuarios.serializers import TokenDeSesionSerializer, UsuarioSerializer

    refresco = TokenDeSesionSerializer.get_token(usuario)
    if ajustes_jwt.UPDATE_LAST_LOGIN:
        update_last_login(None, usuario)
    return {
        "refresh": str(refresco),
        "access": str(refresco.access_token),
        "usuario": UsuarioSerializer(usuario).data,
    }


def crear_desafio(usuario: Usuario) -> str:
    # La huella del secreto va dentro: si la persona desactiva y vuelve a
    # activar la verificación, un desafío viejo deja de servir.
    return signing.TimestampSigner(salt=SAL_DEL_DESAFIO).sign_object(
        {"u": usuario.pk, "s": _huella(usuario.otp_secreto)[:12]}
    )


def leer_desafio(desafio: str) -> Usuario | None:
    try:
        datos = signing.TimestampSigner(salt=SAL_DEL_DESAFIO).unsign_object(
            desafio, max_age=VIGENCIA_DEL_DESAFIO
        )
    except signing.BadSignature:
        return None
    usuario = Usuario.objects.filter(pk=datos.get("u"), is_active=True).first()
    if usuario is None or not pide_codigo(usuario):
        return None
    if datos.get("s") != _huella(usuario.otp_secreto)[:12]:
        return None
    return usuario


# ── Códigos ─────────────────────────────────────────────────────────────────


def _huella(valor: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(), valor.encode(), hashlib.sha256
    ).hexdigest()


def _normalizar(codigo: str) -> str:
    return "".join(
        caracter for caracter in (codigo or "") if caracter.isalnum()
    ).lower()


def nuevos_codigos_de_respaldo() -> tuple[list[str], list[str]]:
    """Los códigos para mostrar una vez, y sus huellas para guardar."""
    legibles = []
    for _ in range(CANTIDAD_DE_RESPALDO):
        crudo = secrets.token_hex(5)
        legibles.append(f"{crudo[:5]}-{crudo[5:]}")
    return legibles, [_huella(_normalizar(codigo)) for codigo in legibles]


def _codigo_de_la_app_vale(secreto: str, codigo: str, *, clave_de_uso: str) -> bool:
    limpio = _normalizar(codigo)
    if len(limpio) != 6 or not limpio.isdigit():
        return False
    if not pyotp.TOTP(secreto).verify(limpio, valid_window=1):
        return False
    # Un mismo código no entra dos veces mientras sigue vigente.
    return cache.add(f"otp-usado:{clave_de_uso}:{limpio}", 1, timeout=120)


def verificar(usuario: Usuario, codigo: str) -> bool:
    """
    Si el código de la app (o uno de respaldo) es válido para esta cuenta.

    Un código de respaldo se consume al usarse.
    """
    if _codigo_de_la_app_vale(
        usuario.otp_secreto, codigo, clave_de_uso=str(usuario.pk)
    ):
        return True

    huella = _huella(_normalizar(codigo))
    if huella in (usuario.otp_respaldo or []):
        usuario.otp_respaldo = [h for h in usuario.otp_respaldo if h != huella]
        usuario.save(update_fields=["otp_respaldo"])
        return True
    return False


def _clave_de_fallos(usuario: Usuario) -> str:
    return f"otp-fallos:{usuario.pk}"


def bloqueado(usuario: Usuario) -> bool:
    return (cache.get(_clave_de_fallos(usuario)) or 0) >= MAXIMO_DE_FALLOS


def anotar_fallo(usuario: Usuario) -> None:
    clave = _clave_de_fallos(usuario)
    if not cache.add(clave, 1, timeout=ESPERA_TRAS_FALLOS):
        try:
            cache.incr(clave)
        except ValueError:
            cache.set(clave, 1, timeout=ESPERA_TRAS_FALLOS)


def olvidar_fallos(usuario: Usuario) -> None:
    cache.delete(_clave_de_fallos(usuario))


def qr_en_svg(uri: str) -> str:
    imagen = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage, box_size=10)
    salida = io.BytesIO()
    imagen.save(salida)
    return "data:image/svg+xml;base64," + base64.b64encode(salida.getvalue()).decode()


# ── Vistas ──────────────────────────────────────────────────────────────────


class _ConLimite:
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "autenticacion"


class CodigoSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=20)


class VerificarAlEntrar(_ConLimite, APIView):
    """POST /auth/sesion/otp  {"desafio": ..., "codigo": "123456"} → tokens."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        datos = CodigoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        usuario = leer_desafio(str(request.data.get("desafio", "")))
        if usuario is None:
            raise serializers.ValidationError(
                {"general": "La verificación venció. Vuelve a ingresar tu contraseña."}
            )
        if bloqueado(usuario):
            return Response(
                {
                    "detail": "Demasiados códigos incorrectos. "
                    "Espera unos minutos e intenta de nuevo."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        if not verificar(usuario, datos.validated_data["codigo"]):
            anotar_fallo(usuario)
            raise serializers.ValidationError(
                {"codigo": "El código no es válido o ya venció."}
            )

        olvidar_fallos(usuario)
        registrar(
            Accion.SESION,
            "sesión",
            usuario.email,
            tienda=usuario.tienda,
            usuario=usuario,
        )
        return Response(tokens_para(usuario))


class _SoloQuienAdministra(IsAuthenticated):
    message = "La verificación en dos pasos es para cuentas de dueño o administración."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and aplica(request.user)


class EstadoDosPasos(APIView):
    """GET /auth/otp: si está activa y cuántos códigos de respaldo quedan."""

    permission_classes = [_SoloQuienAdministra]

    def get(self, request):
        usuario = request.user
        return Response(
            {
                "activa": pide_codigo(usuario),
                "codigosDeRespaldo": len(usuario.otp_respaldo or [])
                if usuario.otp_activo
                else 0,
            }
        )


class IniciarDosPasos(_ConLimite, APIView):
    """POST /auth/otp/iniciar: secreto nuevo y su QR. Todavía no queda activa."""

    permission_classes = [_SoloQuienAdministra]

    def post(self, request):
        usuario = request.user
        if usuario.otp_activo:
            raise serializers.ValidationError(
                {"general": "La verificación en dos pasos ya está activa."}
            )
        secreto = pyotp.random_base32()
        usuario.otp_secreto = secreto
        usuario.save(update_fields=["otp_secreto"])
        uri = pyotp.TOTP(secreto).provisioning_uri(
            name=usuario.email, issuer_name=EMISOR
        )
        return Response({"secreto": secreto, "qr": qr_en_svg(uri)})


class ConfirmarDosPasos(_ConLimite, APIView):
    """POST /auth/otp/confirmar {"codigo"}: la activa y entrega los de respaldo."""

    permission_classes = [_SoloQuienAdministra]

    def post(self, request):
        usuario = request.user
        datos = CodigoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        if usuario.otp_activo:
            raise serializers.ValidationError(
                {"general": "La verificación en dos pasos ya está activa."}
            )
        if not usuario.otp_secreto or not _codigo_de_la_app_vale(
            usuario.otp_secreto,
            datos.validated_data["codigo"],
            clave_de_uso=f"alta-{usuario.pk}",
        ):
            raise serializers.ValidationError(
                {"codigo": "El código no coincide. Revisa la hora del teléfono."}
            )

        legibles, huellas = nuevos_codigos_de_respaldo()
        usuario.otp_activo = True
        usuario.otp_respaldo = huellas
        usuario.save(update_fields=["otp_activo", "otp_respaldo"])
        registrar(
            Accion.CUENTA,
            "cuenta",
            usuario.email,
            tienda=usuario.tienda,
            usuario=usuario,
            detalle={"verificación en dos pasos": ["inactiva", "activa"]},
        )
        return Response({"codigosDeRespaldo": legibles})


class DesactivarSerializer(CodigoSerializer):
    password = serializers.CharField(write_only=True)


class DesactivarDosPasos(_ConLimite, APIView):
    """POST /auth/otp/desactivar {"password", "codigo"}."""

    permission_classes = [_SoloQuienAdministra]

    def post(self, request):
        usuario = request.user
        datos = DesactivarSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        if not usuario.check_password(datos.validated_data["password"]):
            raise serializers.ValidationError(
                {"password": "La contraseña no es correcta."}
            )
        if not pide_codigo(usuario):
            raise serializers.ValidationError(
                {"general": "La verificación en dos pasos no está activa."}
            )
        if not verificar(usuario, datos.validated_data["codigo"]):
            raise serializers.ValidationError({"codigo": "El código no es válido."})

        usuario.otp_activo = False
        usuario.otp_secreto = ""
        usuario.otp_respaldo = []
        usuario.save(update_fields=["otp_activo", "otp_secreto", "otp_respaldo"])
        registrar(
            Accion.CUENTA,
            "cuenta",
            usuario.email,
            tienda=usuario.tienda,
            usuario=usuario,
            detalle={"verificación en dos pasos": ["activa", "inactiva"]},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
