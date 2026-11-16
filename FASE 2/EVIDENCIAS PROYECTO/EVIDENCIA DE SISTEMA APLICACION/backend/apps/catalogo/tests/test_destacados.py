"""Los carruseles de la portada: más vendidos y recién llegados."""

from decimal import Decimal

import pytest

from apps.pedidos.models import LineaPedido, Pedido

pytestmark = pytest.mark.django_db


def _vender(producto, neto, estado=Pedido.Estado.ENTREGADO):
    pedido = Pedido.objects.create(
        tienda=producto.tienda,
        nombre_contacto="Ana",
        telefono_contacto="+56900000000",
        estado=estado,
    )
    LineaPedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=Decimal("1"),
        precio_unitario_neto=Decimal(neto),
        subtotal_neto=Decimal(neto),
        subtotal_iva=Decimal("0"),
        subtotal_total=Decimal(neto),
    )


def test_sin_ventas_no_hay_mas_vendidos_pero_si_nuevos(client, producto_a):
    respuesta = client.get(f"/api/t/{producto_a.tienda.slug}/destacados")

    assert respuesta.status_code == 200
    assert respuesta.json()["masVendidos"] == []
    assert [p["codigo"] for p in respuesta.json()["nuevos"]] == [producto_a.codigo]


def test_ordena_por_lo_vendido_e_ignora_lo_anulado(client, tienda_a, crear_producto):
    poco = crear_producto(tienda_a, codigo="POCO")
    mucho = crear_producto(tienda_a, codigo="MUCHO")
    _vender(poco, "1000")
    _vender(mucho, "9000")
    _vender(poco, "50000", estado=Pedido.Estado.CANCELADO)

    respuesta = client.get(f"/api/t/{tienda_a.slug}/destacados")

    assert [p["codigo"] for p in respuesta.json()["masVendidos"]] == ["MUCHO", "POCO"]


def test_las_ventas_de_otra_tienda_no_cuentan(client, producto_a, producto_b):
    # Las dos fixtures comparten código; lo que importa es que una venta de la
    # tienda B no ponga nada en el ranking de la A.
    _vender(producto_b, "9000")

    respuesta = client.get(f"/api/t/{producto_a.tienda.slug}/destacados")

    assert respuesta.json()["masVendidos"] == []
