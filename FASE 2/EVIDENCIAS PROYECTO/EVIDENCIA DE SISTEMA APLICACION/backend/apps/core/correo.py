"""
El envío de correos de la plataforma, en un solo lugar.

Lo usan la recuperación de contraseña y los avisos de la agenda. Está acá y no
en cada app para que el día que cambie el proveedor —o se verifique el dominio
en Resend— cambie en un solo archivo.
"""

import json
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import send_mail


def enviar_correo(destino: str, asunto: str, texto: str) -> None:
    """
    Manda el correo.

    Con `RESEND_API_KEY` sale por la API HTTP de Resend: varios hostings
    bloquean el puerto SMTP. Sin ella usa el backend de correo de Django, que en
    desarrollo lo escribe en la consola.

    Lanza una excepción si el envío falla: quien llama decide si eso se le
    muestra a alguien o solo queda registrado.
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
