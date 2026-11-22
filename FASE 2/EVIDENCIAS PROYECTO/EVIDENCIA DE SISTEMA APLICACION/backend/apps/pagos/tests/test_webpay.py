"""
Pago con Webpay Plus: crear, volver y en qué queda el pedido.

Transbank se reemplaza por un falso: se prueba que el pedido quede confirmado
solo si Transbank autoriza el monto exacto, que un pago rechazado, anulado o
vencido devuelva el stock, que WhatsApp siga funcionando igual, y que una
tienda sin Webpay no lo ofrezca.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.pagos import servicios, webpay
from apps.pagos.models import EstadoDelPago, Pago
from apps.pedidos.models import Pedido

pytestmark = pytest.mark.django_db

CONTACTO = {
    "nombre_contacto": "Yerko Pérez",
    "telefono_contacto": "+56 9 1234 5678",
    "rut_contacto": "11.111.111-1",
    "email_contacto": "yerko@example.com",
}


class TransbankFalso:
    """Responde como la API v1.2 y anota lo que se le pidió."""

    def __init__(self):
        self.llamadas = []
        self.resultado = "AUTHORIZED"
        self.monto = None
        self.caido = False

    def __call__(self, metodo, ruta, cuerpo=None):
        self.llamadas.append((metodo, ruta, cuerpo))
        if self.caido:
            raise webpay.ErrorDeWebpay("sin conexión")
        if metodo == "POST":
            self.monto = cuerpo["amount"]
            return {
                "token": f"tok-{len(self.llamadas)}",
                "url": "https://webpay3gint.transbank.cl/webpayserver/initTransaction",
            }
        return {
            "status": self.resultado,
            "response_code": 0 if self.resultado == "AUTHORIZED" else -1,
            "amount": self.monto,
            "authorization_code": "1213",
            "card_detail": {"card_number": "6623"},
        }


@pytest.fixture
def transbank(monkeypatch):
    falso = TransbankFalso()
    monkeypatch.setattr(webpay, "_llamar", falso)
    return falso


@pytest.fixture
def con_webpay(tienda_a):
    tienda_a.acepta_webpay = True
    tienda_a.save()
    return tienda_a


def pedir(client, tienda, producto, metodo="webpay", cantidad="2"):
    return client.post(
        f"/api/t/{tienda.slug}/pedidos",
        {
            **CONTACTO,
            "metodo": metodo,
            "lineas": [{"codigo": producto.codigo, "cantidad": cantidad}],
        },
        content_type="application/json",
        SERVER_NAME="localhost",
    )


def volver(client, **datos):
    return client.post("/api/pagos/webpay/retorno", datos, SERVER_NAME="localhost")


def test_con_webpay_se_reserva_el_pedido_y_se_entrega_la_url(
    client, con_webpay, producto_a, transbank
):
    respuesta = pedir(client, con_webpay, producto_a)

    assert respuesta.status_code == 201, respuesta.json()
    cuerpo = respuesta.json()
    assert cuerpo["webpay"]["url"].startswith("https://webpay3gint.transbank.cl")
    pedido = Pedido.objects.get(folio=cuerpo["numero"])
    assert pedido.estado == Pedido.Estado.PENDIENTE
    producto_a.refresh_from_db()
    assert producto_a.stock == Decimal("23")
    # El monto que se le pide a Transbank es el total del pedido, en pesos.
    assert transbank.llamadas[0][2]["amount"] == int(pedido.total)
    assert transbank.llamadas[0][2]["return_url"].endswith("/api/pagos/webpay/retorno")


def test_pago_autorizado_confirma_el_pedido(client, con_webpay, producto_a, transbank):
    cuerpo = pedir(client, con_webpay, producto_a).json()

    respuesta = volver(client, token_ws=cuerpo["webpay"]["token"])

    assert respuesta.status_code == 302
    assert (
        f"/t/{con_webpay.slug}/pago?folio={cuerpo['numero']}" in respuesta["Location"]
    )
    pedido = Pedido.objects.get(folio=cuerpo["numero"])
    assert pedido.estado == Pedido.Estado.CONFIRMADO
    pago = pedido.pagos.get()
    assert pago.estado == EstadoDelPago.AUTORIZADO
    assert pago.ultimos_digitos == "6623"


def test_volver_dos_veces_no_confirma_dos_veces(
    client, con_webpay, producto_a, transbank
):
    token = pedir(client, con_webpay, producto_a).json()["webpay"]["token"]

    volver(client, token_ws=token)
    volver(client, token_ws=token)

    confirmaciones = [llamada for llamada in transbank.llamadas if llamada[0] == "PUT"]
    assert len(confirmaciones) == 1


def test_pago_rechazado_anula_y_devuelve_el_stock(
    client, con_webpay, producto_a, transbank
):
    transbank.resultado = "FAILED"
    cuerpo = pedir(client, con_webpay, producto_a).json()

    volver(client, token_ws=cuerpo["webpay"]["token"])

    pedido = Pedido.objects.get(folio=cuerpo["numero"])
    assert pedido.estado == Pedido.Estado.CANCELADO
    producto_a.refresh_from_db()
    assert producto_a.stock == Decimal("25")


def test_un_monto_distinto_no_se_da_por_pagado(
    client, con_webpay, producto_a, transbank
):
    cuerpo = pedir(client, con_webpay, producto_a).json()
    transbank.monto = 1  # Transbank informa otro monto

    volver(client, token_ws=cuerpo["webpay"]["token"])

    pedido = Pedido.objects.get(folio=cuerpo["numero"])
    assert pedido.estado == Pedido.Estado.CANCELADO


def test_anulado_en_webpay_devuelve_el_stock(client, con_webpay, producto_a, transbank):
    cuerpo = pedir(client, con_webpay, producto_a).json()

    volver(
        client, TBK_TOKEN=cuerpo["webpay"]["token"], TBK_ORDEN_COMPRA=cuerpo["numero"]
    )

    pedido = Pedido.objects.get(folio=cuerpo["numero"])
    assert pedido.estado == Pedido.Estado.CANCELADO
    assert pedido.pagos.get().estado == EstadoDelPago.ABORTADO
    producto_a.refresh_from_db()
    assert producto_a.stock == Decimal("25")


def test_un_pago_que_no_vuelve_vence(client, con_webpay, producto_a, transbank):
    cuerpo = pedir(client, con_webpay, producto_a).json()
    Pago.objects.update(fecha_creacion=timezone.now() - timedelta(minutes=20))

    assert servicios.anular_vencidos() == 1

    pedido = Pedido.objects.get(folio=cuerpo["numero"])
    assert pedido.estado == Pedido.Estado.CANCELADO
    producto_a.refresh_from_db()
    assert producto_a.stock == Decimal("25")


def test_si_transbank_no_responde_no_queda_pedido(
    client, con_webpay, producto_a, transbank
):
    transbank.caido = True

    respuesta = pedir(client, con_webpay, producto_a)

    assert respuesta.status_code == 502
    assert not Pedido.objects.exists()
    producto_a.refresh_from_db()
    assert producto_a.stock == Decimal("25")


def test_una_tienda_sin_webpay_no_lo_ofrece(client, tienda_a, producto_a, transbank):
    respuesta = pedir(client, tienda_a, producto_a)

    assert respuesta.status_code == 400
    assert transbank.llamadas == []


def test_whatsapp_sigue_igual(client, con_webpay, producto_a, transbank):
    respuesta = pedir(client, con_webpay, producto_a, metodo="whatsapp")

    assert respuesta.status_code == 201
    assert "webpay" not in respuesta.json()
    assert transbank.llamadas == []


def test_la_bandeja_muestra_el_pago(client, con_webpay, producto_a, transbank, dueno_a):
    from rest_framework_simplejwt.tokens import AccessToken

    token = pedir(client, con_webpay, producto_a).json()["webpay"]["token"]
    volver(client, token_ws=token)

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(dueno_a)}"
    (pedido,) = client.get("/api/panel/pedidos/", SERVER_NAME="localhost").json()

    assert pedido["pago"]["estado"] == "autorizado"
    assert pedido["pago"]["ultimosDigitos"] == "6623"
