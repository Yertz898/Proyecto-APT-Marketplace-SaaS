"""Comprar sin cuenta pide RUT, nombre y correo; con cuenta, no."""

import pytest
from rest_framework.test import APIClient

from apps.pedidos.models import Pedido

pytestmark = pytest.mark.django_db


def _pedido(producto, **contacto):
    return {
        "nombre_contacto": "Ana Soto",
        "telefono_contacto": "+56912345678",
        "lineas": [{"codigo": producto.codigo, "cantidad": "1"}],
        **contacto,
    }


def test_sin_cuenta_y_sin_rut_ni_correo_no_compra(
    client, producto_a, detalles_de_error
):
    respuesta = client.post(
        f"/api/t/{producto_a.tienda.slug}/pedidos",
        _pedido(producto_a),
        content_type="application/json",
    )

    assert respuesta.status_code == 400
    detalles = detalles_de_error(respuesta)
    assert "rut_contacto" in detalles and "email_contacto" in detalles


def test_un_rut_invalido_se_rechaza(client, producto_a):
    respuesta = client.post(
        f"/api/t/{producto_a.tienda.slug}/pedidos",
        _pedido(
            producto_a, rut_contacto="12.345.678-0", email_contacto="ana@ejemplo.cl"
        ),
        content_type="application/json",
    )

    assert respuesta.status_code == 400


def test_como_visitante_queda_guardado_su_rut(client, producto_a):
    respuesta = client.post(
        f"/api/t/{producto_a.tienda.slug}/pedidos",
        _pedido(
            producto_a, rut_contacto="11.111.111-1", email_contacto="ana@ejemplo.cl"
        ),
        content_type="application/json",
    )

    assert respuesta.status_code in (200, 201)
    pedido = Pedido.objects.get()
    assert pedido.rut_contacto == "11111111-1"
    assert pedido.comprador is None


def test_con_cuenta_no_se_le_pide_el_rut(comprador, producto_a):
    from rest_framework_simplejwt.tokens import AccessToken

    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(comprador)}")
    respuesta = cliente.post(
        f"/api/t/{producto_a.tienda.slug}/pedidos", _pedido(producto_a), format="json"
    )

    assert respuesta.status_code in (200, 201)
    assert Pedido.objects.get().comprador == comprador
