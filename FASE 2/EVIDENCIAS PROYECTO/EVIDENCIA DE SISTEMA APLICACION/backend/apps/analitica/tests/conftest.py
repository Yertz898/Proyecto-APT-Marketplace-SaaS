"""
Lo que comparten las pruebas de analítica: pedidos con fecha a elección.

Casi todo lo que se mide acá depende de **cuándo** pasó algo —el mes en
curso, los últimos noventa días, cuántos días lleva un cliente sin volver—,
así que poder fechar un pedido hacia atrás es el requisito de base.
"""

from datetime import date, timedelta
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
    Una venta fechada N **meses de calendario** atrás, el día 15.

    De calendario y no de treinta días: treinta días no son un mes y el error
    se acumula. Retrocediendo seis veces treinta días desde noviembre, dos de
    las fechas caen en mayo, el producto queda con cinco meses distintos en
    vez de seis y el pronóstico se niega a proyectar. La prueba entonces falla
    o pasa según el día en que se corra, que es la peor clase de prueba.

    El día 15 por la misma razón de antes: lejos de los dos bordes del mes,
    así ni el corte ni la zona horaria cambian en qué mes cae.
    """

    def _crear(tienda, producto, meses, **extra):
        hoy = timezone.localdate()
        # El mes como número absoluto hace el retroceso sin casos especiales
        # en enero.
        total = hoy.year * 12 + (hoy.month - 1) - meses
        objetivo = date(total // 12, total % 12 + 1, 15)
        return crear_pedido(tienda, producto, hace_dias=(hoy - objetivo).days, **extra)

    return _crear
