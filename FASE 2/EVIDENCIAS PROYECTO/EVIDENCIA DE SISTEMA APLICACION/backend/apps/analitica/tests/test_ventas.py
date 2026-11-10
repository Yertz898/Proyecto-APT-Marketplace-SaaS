"""
Los indicadores de ventas del panel.

Lo que más se prueba acá es **qué no se cuenta**: un pedido pendiente todavía
no es una venta, uno anulado no lo fue nunca, y un producto recién publicado
no es un producto detenido. Si esas tres se cuentan mal, los números igual
salen y nadie se entera de que están inflados.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.analitica import ventas
from apps.pedidos.models import LineaPedido, Pedido

pytestmark = pytest.mark.django_db

VENTAS = "/api/panel/ventas"


def como(client, usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


@pytest.fixture
def crear_pedido(db):
    """
    Un pedido con una línea, con fecha y estado a elección.

    La fecha se reescribe con `update` porque `fecha_creacion` es
    `auto_now_add` y no se puede fijar al crear.
    """

    def _crear(tienda, producto, *, cantidad=1, neto=1000, estado=None, hace_dias=0):
        estado = estado or Pedido.Estado.CONFIRMADO
        iva = round(neto * 0.19)
        pedido = Pedido.objects.create(
            tienda=tienda,
            nombre_contacto="Compradora",
            telefono_contacto="+56900000000",
            total_neto=neto,
            total_iva=iva,
            total=neto + iva,
            estado=estado,
        )
        LineaPedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=Decimal(cantidad),
            precio_unitario_neto=neto // cantidad,
            subtotal_neto=neto,
            subtotal_iva=iva,
            subtotal_total=neto + iva,
        )
        if hace_dias:
            Pedido.objects.filter(pk=pedido.pk).update(
                fecha_creacion=timezone.now() - timedelta(days=hace_dias)
            )
            pedido.refresh_from_db()
        return pedido

    return _crear


# ── Qué cuenta como venta ───────────────────────────────────────────────────


def test_sin_pedidos_los_indicadores_quedan_en_cero(tienda_a):
    datos = ventas.resumen(tienda_a)

    assert datos["ventas"] == {"pedidos": 0, "neto": 0, "iva": 0, "total": 0}
    assert datos["masVendidos"] == []
    assert datos["porCoordinar"]["pedidos"] == 0


def test_un_pedido_confirmado_cuenta_como_venta(tienda_a, producto_a, crear_pedido):
    crear_pedido(tienda_a, producto_a, neto=10_000)

    datos = ventas.resumen(tienda_a)

    assert datos["ventas"]["pedidos"] == 1
    assert datos["ventas"]["neto"] == 10_000


def test_un_pedido_pendiente_no_es_una_venta(tienda_a, producto_a, crear_pedido):
    """
    El pago se coordina fuera de la plataforma: entre confirmar el pedido y
    pagar puede no pasar nada. Contarlo como venta infla el mes.
    """
    crear_pedido(tienda_a, producto_a, neto=10_000, estado=Pedido.Estado.PENDIENTE)

    datos = ventas.resumen(tienda_a)

    assert datos["ventas"]["pedidos"] == 0
    assert datos["porCoordinar"]["pedidos"] == 1
    assert datos["porCoordinar"]["total"] == 11_900


def test_un_pedido_anulado_no_cuenta_nunca(tienda_a, producto_a, crear_pedido):
    crear_pedido(tienda_a, producto_a, neto=10_000, estado=Pedido.Estado.CANCELADO)

    datos = ventas.resumen(tienda_a)

    assert datos["ventas"]["pedidos"] == 0
    assert datos["porCoordinar"]["pedidos"] == 0
    assert datos["masVendidos"] == []


def test_un_pedido_entregado_cuenta_como_venta(tienda_a, producto_a, crear_pedido):
    crear_pedido(tienda_a, producto_a, neto=10_000, estado=Pedido.Estado.ENTREGADO)

    assert ventas.resumen(tienda_a)["ventas"]["pedidos"] == 1


# ── El mes y su comparación ─────────────────────────────────────────────────


def test_sin_mes_anterior_no_hay_porcentaje_que_mostrar(
    tienda_a, producto_a, crear_pedido
):
    """
    «+100%» contra un mes sin ventas es una comparación inventada.
    """
    crear_pedido(tienda_a, producto_a, neto=10_000)

    assert ventas.resumen(tienda_a)["mesAnterior"]["variacion"] is None


def test_una_venta_de_hace_un_ano_no_entra_en_el_mes(
    tienda_a, producto_a, crear_pedido
):
    crear_pedido(tienda_a, producto_a, neto=10_000, hace_dias=400)

    assert ventas.resumen(tienda_a)["ventas"]["pedidos"] == 0


# ── Los más vendidos ────────────────────────────────────────────────────────


def test_los_mas_vendidos_se_ordenan_por_dinero_y_no_por_unidades(
    tienda_a, crear_producto, crear_pedido
):
    """
    Diez lotes baratos no valen lo mismo que dos caros, y el dueño reparte su
    atención por lo que deja plata.
    """
    barato = crear_producto(tienda_a, codigo="BARATO", stock=Decimal("100"))
    caro = crear_producto(tienda_a, codigo="CARO", stock=Decimal("100"))
    crear_pedido(tienda_a, barato, cantidad=10, neto=10_000)
    crear_pedido(tienda_a, caro, cantidad=2, neto=90_000)

    mejores = ventas.resumen(tienda_a)["masVendidos"]

    assert [m["codigo"] for m in mejores] == ["CARO", "BARATO"]


def test_los_mas_vendidos_ignoran_lo_anulado(tienda_a, crear_producto, crear_pedido):
    uno = crear_producto(tienda_a, codigo="A-1", stock=Decimal("50"))
    crear_pedido(tienda_a, uno, neto=90_000, estado=Pedido.Estado.CANCELADO)

    assert ventas.resumen(tienda_a)["masVendidos"] == []


# ── Los que no se mueven ────────────────────────────────────────────────────


def test_un_producto_sin_ventas_aparece_como_detenido(tienda_a, crear_producto):
    quieto = crear_producto(tienda_a, codigo="QUIETO")
    _envejecer(quieto, dias=120)

    detenidos = ventas.resumen(tienda_a)["sinMovimiento"]

    assert [d["codigo"] for d in detenidos] == ["QUIETO"]
    assert detenidos[0]["diasSinVender"] is None


def test_un_producto_recien_publicado_no_es_un_producto_detenido(
    tienda_a, crear_producto
):
    """Nunca tuvo tiempo de venderse; marcarlo empujaría a rebajarlo de más."""
    crear_producto(tienda_a, codigo="NUEVO")

    assert ventas.resumen(tienda_a)["sinMovimiento"] == []


def test_un_producto_desactivado_no_aparece_como_detenido(tienda_a, crear_producto):
    """Ya está fuera de la vitrina: no hay nada que decidir sobre él."""
    apagado = crear_producto(tienda_a, codigo="APAGADO", activo=False)
    _envejecer(apagado, dias=120)

    assert ventas.resumen(tienda_a)["sinMovimiento"] == []


def test_un_producto_vendido_en_la_ventana_no_esta_detenido(
    tienda_a, crear_producto, crear_pedido
):
    vendido = crear_producto(tienda_a, codigo="VENDIDO", stock=Decimal("50"))
    _envejecer(vendido, dias=120)
    crear_pedido(tienda_a, vendido, neto=5_000, hace_dias=10)

    assert ventas.resumen(tienda_a)["sinMovimiento"] == []


def test_el_detenido_dice_hace_cuanto_fue_su_ultima_venta(
    tienda_a, crear_producto, crear_pedido
):
    """
    «Nunca se vendió» y «no se vende hace cinco meses» son dos problemas
    distintos y la pantalla los dice distinto.
    """
    producto = crear_producto(tienda_a, codigo="ANTIGUO", stock=Decimal("50"))
    _envejecer(producto, dias=300)
    crear_pedido(tienda_a, producto, neto=5_000, hace_dias=150)

    detenido = ventas.resumen(tienda_a)["sinMovimiento"][0]

    assert detenido["codigo"] == "ANTIGUO"
    assert 149 <= detenido["diasSinVender"] <= 151


# ── Aislamiento ─────────────────────────────────────────────────────────────


def test_una_tienda_no_ve_las_ventas_de_la_otra(
    tienda_a, tienda_b, producto_b, crear_pedido
):
    crear_pedido(tienda_b, producto_b, neto=99_000)

    assert ventas.resumen(tienda_a)["ventas"]["pedidos"] == 0
    assert ventas.resumen(tienda_b)["ventas"]["pedidos"] == 1


def test_el_endpoint_devuelve_solo_la_tienda_del_token(
    client, tienda_a, tienda_b, dueno_a, producto_a, producto_b, crear_pedido
):
    crear_pedido(tienda_a, producto_a, neto=10_000)
    crear_pedido(tienda_b, producto_b, neto=99_000)

    cuerpo = como(client, dueno_a).get(VENTAS).json()

    assert cuerpo["ventas"]["pedidos"] == 1
    assert cuerpo["ventas"]["neto"] == 10_000


def test_el_endpoint_pide_sesion(client):
    assert client.get(VENTAS).status_code in (401, 403)


def test_un_comprador_no_puede_ver_las_ventas(client, comprador):
    assert como(client, comprador).get(VENTAS).status_code == 403


def _envejecer(producto, dias):
    """Mueve la fecha de publicación hacia atrás; `auto_now_add` no se fija al crear."""
    from apps.catalogo.models import Producto

    Producto.objects.filter(pk=producto.pk).update(
        fecha_creacion=timezone.now() - timedelta(days=dias)
    )
