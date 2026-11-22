"""
Cliente de la API REST de Webpay Plus (Transbank), versión 1.2.

Se habla directo con la API por HTTP, como con Resend, en vez de usar el SDK
oficial: son dos llamadas (crear y confirmar) y así no se depende de que el
SDK funcione con Python 3.14.

Por omisión apunta al **ambiente de integración** con las credenciales de
prueba públicas de Transbank: no se cobra nada y se paga con las tarjetas de
prueba que publica Transbank. Para cobrar de verdad hace falta un contrato con
Transbank, su código de comercio y su llave, y `WEBPAY_AMBIENTE=produccion`.
"""

import json
import urllib.error
import urllib.request

from django.conf import settings

RUTA = "/rswebpaytransaction/api/webpay/v1.2/transactions"

SERVIDORES = {
    "integracion": "https://webpay3gint.transbank.cl",
    "produccion": "https://webpay3g.transbank.cl",
}


class ErrorDeWebpay(Exception):
    """Transbank no respondió o respondió con un error."""


def _llamar(metodo: str, ruta: str, cuerpo: dict | None = None) -> dict:
    servidor = SERVIDORES.get(settings.WEBPAY_AMBIENTE, SERVIDORES["integracion"])
    peticion = urllib.request.Request(
        servidor + ruta,
        data=json.dumps(cuerpo).encode() if cuerpo is not None else None,
        method=metodo,
        headers={
            "Tbk-Api-Key-Id": settings.WEBPAY_CODIGO_COMERCIO,
            "Tbk-Api-Key-Secret": settings.WEBPAY_API_KEY,
            "Content-Type": "application/json",
            "User-Agent": "DealCommerce/1.0",
        },
    )
    try:
        with urllib.request.urlopen(peticion, timeout=20) as respuesta:  # noqa: S310 — URL fija
            contenido = respuesta.read()
    except urllib.error.HTTPError as error:
        motivo = error.read()[:300].decode(errors="replace")
        raise ErrorDeWebpay(f"Transbank respondió {error.code}: {motivo}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise ErrorDeWebpay(f"No se pudo hablar con Transbank: {error}") from error
    return json.loads(contenido or b"{}")


def crear(orden_compra: str, sesion: str, monto: int, url_retorno: str) -> dict:
    """Abre la transacción. Devuelve {"token", "url"} para mandar al cliente."""
    return _llamar(
        "POST",
        RUTA,
        {
            "buy_order": orden_compra[:26],
            "session_id": sesion[:61],
            "amount": monto,
            "return_url": url_retorno,
        },
    )


def confirmar(token: str) -> dict:
    """
    Confirma (commit) la transacción al volver el cliente.

    Hay que hacerlo para que el cobro quede firme: una transacción autorizada
    que no se confirma, Transbank la reversa sola.
    """
    return _llamar("PUT", f"{RUTA}/{token}")
