"""
«¿Olvidaste tu contraseña?»: el enlace por correo y la contraseña nueva.

Sirve para cualquier cuenta —comprador, dueño, vendedor—, porque el correo es
único en toda la plataforma. Lo único que cambia es a qué página lleva el
enlace: quien lo pidió desde una tienda vuelve a esa tienda, con su aspecto; el
resto vuelve al acceso de DealCommerce.

Dos reglas de seguridad:

- **No se revela si el correo tiene cuenta.** La respuesta es la misma exista
  o no, para que el formulario no sirva para averiguar quién está registrado.
- **El enlace vale una vez y por poco tiempo.** El token es el de Django, que
  se calcula con la contraseña actual: apenas se cambia, deja de servir. Vence
  a la hora (`PASSWORD_RESET_TIMEOUT`).
"""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.auditoria.models import Accion
from apps.auditoria.registrar import registrar
from apps.tiendas.models import Tienda
from apps.usuarios.models import Usuario

logger = logging.getLogger(__name__)

RESPUESTA_NEUTRA = {
    "detalle": (
        "Si ese correo tiene una cuenta, te enviamos un enlace para crear una "
        "contraseña nueva."
    )
}


def _enlace(usuario: Usuario, tienda: Tienda | None) -> str:
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = default_token_generator.make_token(usuario)
    ruta = f"/t/{tienda.slug}/restablecer" if tienda else "/panel/restablecer"
    return f"{settings.FRONTEND_URL}{ruta}?uid={uid}&token={token}"


def _enviar(destino: str, asunto: str, texto: str) -> None:
    """
    Manda el correo.

    Con `RESEND_API_KEY` sale por la API HTTP de Resend: varios hostings
    bloquean el puerto SMTP. Sin ella usa el backend de correo de Django, que en
    desarrollo lo escribe en la consola.
    """
    if settings.RESEND_API_KEY:
        cuerpo = json.dumps(
            {
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [destino],
                "subject": asunto,
                "text": texto,
            }
        ).encode()
        peticion = urllib.request.Request(
            "https://api.resend.com/emails",
            data=cuerpo,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
                # Sin esto urllib se presenta como «Python-urllib/3.x», y el
                # cortafuegos de Resend lo rechaza con un 403 «error code:
                # 1010» antes de mirar la clave.
                "User-Agent": "DealCommerce/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(peticion, timeout=10):  # noqa: S310 — URL fija
                return
        except urllib.error.HTTPError as error:
            # El motivo viene en el cuerpo («API key is invalid», «domain is
            # not verified»…): sin él, el log solo diría «403 Forbidden».
            motivo = error.read()[:300].decode(errors="replace")
            raise RuntimeError(f"Resend respondió {error.code}: {motivo}") from error
    send_mail(asunto, texto, settings.DEFAULT_FROM_EMAIL, [destino])


class PedirEnlaceSerializer(serializers.Serializer):
    email = serializers.EmailField()
    # La tienda desde la que se pidió, para que el enlace vuelva a ella.
    tienda = serializers.SlugField(required=False, allow_blank=True)


class PedirEnlace(APIView):
    """POST /auth/contrasena/olvido: manda el enlace, si el correo tiene cuenta."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "autenticacion"

    def post(self, request):
        datos = PedirEnlaceSerializer(data=request.data)
        datos.is_valid(raise_exception=True)

        usuario = Usuario.objects.filter(
            email__iexact=datos.validated_data["email"], is_active=True
        ).first()
        if usuario is None:
            return Response(RESPUESTA_NEUTRA)

        slug = datos.validated_data.get("tienda") or ""
        tienda = Tienda.objects.filter(slug=slug, activa=True).first() if slug else None
        nombre = tienda.nombre if tienda else "DealCommerce"

        texto = (
            f"Hola {usuario.nombre}:\n\n"
            f"Pediste crear una contraseña nueva para tu cuenta en {nombre}. "
            "Entra a este enlace para elegirla:\n\n"
            f"{_enlace(usuario, tienda)}\n\n"
            "El enlace vence en una hora y sirve una sola vez. Si no fuiste tú, "
            "ignora este correo: tu contraseña sigue siendo la misma.\n"
        )
        try:
            _enviar(usuario.email, f"Tu contraseña de {nombre}", texto)
        except Exception:
            # Al comprador no se le dice nada distinto: sería revelar que el
            # correo tiene cuenta. Queda en el log para revisarlo.
            logger.exception("No se pudo enviar el correo de recuperación")

        return Response(RESPUESTA_NEUTRA)


class RestablecerSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, datos):
        try:
            pk = force_str(urlsafe_base64_decode(datos["uid"]))
            usuario = Usuario.objects.get(pk=pk, is_active=True)
        except (ValueError, TypeError, OverflowError, Usuario.DoesNotExist):
            usuario = None

        if usuario is None or not default_token_generator.check_token(
            usuario, datos["token"]
        ):
            raise serializers.ValidationError(
                {"general": "El enlace venció o ya se usó. Pide uno nuevo."}
            )

        try:
            validate_password(datos["password"], user=usuario)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": error.messages}) from error

        datos["usuario"] = usuario
        return datos


class Restablecer(APIView):
    """POST /auth/contrasena/restablecer: la contraseña nueva, con el enlace."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "autenticacion"

    def post(self, request):
        datos = RestablecerSerializer(data=request.data)
        datos.is_valid(raise_exception=True)

        usuario = datos.validated_data["usuario"]
        usuario.set_password(datos.validated_data["password"])
        usuario.save(update_fields=["password"])
        registrar(
            Accion.CUENTA,
            "contraseña",
            f"{usuario.email} (con el enlace del correo)",
            tienda=usuario.tienda,
            usuario=usuario,
        )
        return Response(
            {
                "email": usuario.email,
                "detalle": "Listo, ya puedes entrar con tu contraseña nueva.",
            },
            status=status.HTTP_200_OK,
        )
