"""La carga de ventas anteriores."""

from datetime import date, timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.catalogo.models import Producto
from apps.pedidos.models import Pedido

pytestmark = pytest.mark.django_db

ENCABEZADO = "fecha,codigo_producto,cantidad,precio_unitario_neto,cliente,pedido\n"


def como(usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(usuario)}")
    return cliente


def _csv(texto):
    return SimpleUploadedFile(
        "ventas.csv", (ENCABEZADO + texto).encode(), content_type="text/csv"
    )


def _validar_y_confirmar(cliente, texto):
    validada = cliente.post(
        "/api/panel/cargas/ventas/validar", {"archivo": _csv(texto)}
    )
    assert validada.status_code == 201, validada.json()
    resumen = validada.json()
    confirmada = cliente.post(f"/api/panel/cargas/{resumen['cargaId']}/confirmar", {})
    assert confirmada.status_code == 200
    return resumen


def test_crea_pedidos_entregados_con_su_fecha_sin_tocar_el_stock(dueno_a, producto_a):
    stock_antes = Producto.objects.get(pk=producto_a.pk).stock

    resumen = _validar_y_confirmar(
        como(dueno_a),
        f"15-03-2026,{producto_a.codigo},2,5000,María,B-1\n"
        f"15-03-2026,{producto_a.codigo},1,5000,María,B-1\n"
        f"02-04-2026,{producto_a.codigo},3,4500,Pedro,\n",
    )

    assert resumen["crear"] == 2
    pedidos = Pedido.objects.filter(tienda=producto_a.tienda).order_by("fecha_creacion")
    assert pedidos.count() == 2
    assert all(p.estado == Pedido.Estado.ENTREGADO for p in pedidos)
    assert pedidos[0].fecha_creacion.date() == date(2026, 3, 15)
    assert pedidos[0].lineas.count() == 2
    assert pedidos[0].total_neto == 15000
    assert Producto.objects.get(pk=producto_a.pk).stock == stock_antes


def test_rechaza_fechas_futuras_y_productos_ajenos(dueno_a, producto_a, producto_b):
    futura = (date.today() + timedelta(days=5)).strftime("%d-%m-%Y")
    cliente = como(dueno_a)

    respuesta = cliente.post(
        "/api/panel/cargas/ventas/validar",
        {
            "archivo": _csv(
                f"{futura},{producto_a.codigo},1,5000,Ana,\n"
                f"01-02-2026,{producto_b.codigo}-OTRO,1,5000,Ana,\n"
            )
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["crear"] == 0
    assert respuesta.json()["rechazar"] == 2


def test_subir_dos_veces_el_mismo_archivo_no_duplica(dueno_a, producto_a):
    cliente = como(dueno_a)
    fila = f"10-01-2026,{producto_a.codigo},2,5000,Luis,\n"

    _validar_y_confirmar(cliente, fila)
    segunda = cliente.post("/api/panel/cargas/ventas/validar", {"archivo": _csv(fila)})

    assert segunda.json()["crear"] == 0
    assert segunda.json()["rechazar"] == 1
    assert Pedido.objects.filter(tienda=producto_a.tienda).count() == 1
