"""
Lo que comparten las pruebas de analítica: pedidos con fecha a elección.

Casi todo lo que se mide acá depende de **cuándo** pasó algo —el mes en
curso, los últimos noventa días, cuántos días lleva un cliente sin volver—,
así que poder fechar un pedido hacia atrás es el requisito de base.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.pedidos.models import LineaPedido, Pedido


@pytest.fixture
def crear_pedido(db):
    """
    Un pedido con una línea, con fecha, cliente y estado a elección.

    La fecha se reescribe con `update` porque `fecha_creacion` es
    `auto_now_add`: Django la pone al guardar y no acepta que se la fijen.
    """

    def _crear(
        tienda,
        producto,
        *,
        cantidad=1,
        neto=1000,
        estado=None,
        hace_dias=0,
        cliente="Compradora",
    ):
        estado = estado or Pedido.Estado.CONFIRMADO
        iva = round(neto * 0.19)
        pedido = Pedido.objects.create(
            tienda=tienda,
            nombre_contacto=cliente,
            telefono_contacto="+56900000000",
            total_neto=neto,
            total_iva=iva,
            total=neto + iva,
            estado=estado,
        )
        LineaPedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=Decimal(str(cantidad)),
            precio_unitario_neto=round(neto / float(cantidad)),
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


@pytest.fixture
def venta_hace_meses(crear_pedido):
    """
    Una venta fechada N meses atrás, a mitad de mes.

    A mitad y no el día 1 ni el 30: así ni el corte del mes ni la zona
    horaria cambian en qué mes cae, que es justo lo que no se quiere estar
    depurando dentro de una prueba de pronóstico.
    """

    def _crear(tienda, producto, meses, **extra):
        return crear_pedido(tienda, producto, hace_dias=meses * 30 + 15, **extra)

    return _crear
