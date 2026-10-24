"""
API pública del catálogo.

La forma de estas respuestas la fija el frontend, que ya está escrito. Si una
clave cambia de nombre acá, la vitrina deja de mostrar el dato sin que nada
falle a gritos: por eso las pruebas afirman sobre el conjunto exacto de claves.

Es un solo endpoint para las tres formas de venta. Lo que no aplica a una forma
viaja en `null`, nunca en otra forma.
"""

from decimal import Decimal

import pytest

from apps.catalogo.models import FormaVenta, UnidadMedida

pytestmark = pytest.mark.django_db

CLAVES = {
    "codigo",
    "nombre",
    "descripcion",
    "categoria",
    "formaVenta",
    "unidadMedida",
    "precioNeto",
    "iva",
    "precioTotal",
    "disponibilidad",
    "agotado",
    "cantidadMinima",
    "piezasTotales",
    "composicion",
    "tramos",
    "minimo",
    "foto",
}


def productos_de(slug):
    return f"/api/t/{slug}/productos"


def producto_de(slug, codigo):
    return f"/api/t/{slug}/productos/{codigo}"


def cotizar_de(slug, codigo):
    return f"/api/t/{slug}/productos/{codigo}/cotizar"


def cotizar(client, slug, codigo, cantidad):
    return client.post(
        cotizar_de(slug, codigo),
        {"cantidad": str(cantidad)},
        content_type="application/json",
    )


# ── Forma de la respuesta ───────────────────────────────────────────────────


def test_el_listado_trae_la_forma_que_espera_la_vitrina(client, tienda_a, producto_a):
    cuerpo = client.get(productos_de(tienda_a.slug)).json()

    assert set(cuerpo) == {"productos", "paginaActual", "totalPaginas"}
    assert set(cuerpo["productos"][0]) == CLAVES


def test_el_producto_trae_el_iva_y_el_total_calculados(
    client, tienda_a, crear_producto
):
    """El navegador no hace aritmética de dinero."""
    crear_producto(tienda_a, codigo="IVA-1", precio_neto=10000)

    cuerpo = client.get(producto_de(tienda_a.slug, "IVA-1")).json()

    assert cuerpo["precioNeto"] == 10000
    assert cuerpo["iva"] == 1900
    assert cuerpo["precioTotal"] == 11900


def test_lo_que_no_aplica_a_la_forma_de_venta_viaja_en_null(
    client, tienda_a, producto_a
):
    cuerpo = client.get(producto_de(tienda_a.slug, producto_a.codigo)).json()

    assert cuerpo["piezasTotales"] is None
    assert cuerpo["composicion"] == []
    assert cuerpo["minimo"] is None
    assert cuerpo["foto"] is None


def test_un_lote_trae_sus_piezas_y_su_composicion(client, tienda_a, lote_a):
    cuerpo = client.get(producto_de(tienda_a.slug, lote_a.codigo)).json()

    assert cuerpo["formaVenta"] == FormaVenta.LOTE
    assert cuerpo["piezasTotales"] == 10
    assert cuerpo["composicion"][0]["cantidad"] == 10


def test_un_producto_por_peso_dice_en_que_unidad_se_mide(client, tienda_a, granel_a):
    cuerpo = client.get(producto_de(tienda_a.slug, granel_a.codigo)).json()

    assert cuerpo["formaVenta"] == FormaVenta.PESO
    assert cuerpo["unidadMedida"] == UnidadMedida.GRAMO


# ── Disponibilidad ──────────────────────────────────────────────────────────


def test_la_ultima_unidad_se_anuncia_aparte(client, tienda_a, crear_producto):
    """«Queda 1» empuja a decidir; el número suelto no dice lo mismo."""
    crear_producto(tienda_a, codigo="ULT-1", stock=Decimal("1"))

    cuerpo = client.get(producto_de(tienda_a.slug, "ULT-1")).json()

    assert cuerpo["disponibilidad"] == {"tipo": "ultima"}


def test_con_varias_unidades_se_dice_cuantas_quedan(client, tienda_a, producto_a):
    cuerpo = client.get(producto_de(tienda_a.slug, producto_a.codigo)).json()

    assert cuerpo["disponibilidad"] == {"tipo": "disponible", "restantes": 25}


def test_lo_que_no_lleva_inventario_lo_dice(client, tienda_a, granel_a):
    """La tienda no sabe cuánto le queda; inventar un número sería mentir."""
    cuerpo = client.get(producto_de(tienda_a.slug, granel_a.codigo)).json()

    assert cuerpo["disponibilidad"] == {"tipo": "sin_control"}
    assert cuerpo["agotado"] is False


# ── Tramos y mínimo ─────────────────────────────────────────────────────────


def test_el_minimo_por_monto_lo_redacta_el_backend(client, tienda_a, granel_a):
    cuerpo = client.get(producto_de(tienda_a.slug, granel_a.codigo)).json()

    assert cuerpo["minimo"] == "Compra mínima de $20.000"


def test_los_tramos_traen_la_forma_que_espera_la_vitrina(client, tienda_a, granel_a):
    tramo = client.get(producto_de(tienda_a.slug, granel_a.codigo)).json()["tramos"][0]

    assert set(tramo) == {"umbral", "unidadUmbral", "precioNeto"}
    assert tramo["umbral"] == 20000


def test_un_producto_sin_tramos_no_tiene_minimo(client, tienda_a, producto_a):
    cuerpo = client.get(producto_de(tienda_a.slug, producto_a.codigo)).json()

    assert cuerpo["tramos"] == []
    assert cuerpo["minimo"] is None


# ── Formas de venta de la tienda ────────────────────────────────────────────


def test_las_formas_de_venta_salen_de_lo_que_la_tienda_vende(
    client, tienda_a, producto_a, granel_a
):
    """La vitrina arma sus pestañas con esto, no con una lista escrita a mano."""
    cuerpo = client.get(f"/api/t/{tienda_a.slug}/formas-de-venta").json()

    assert [f["valor"] for f in cuerpo] == [FormaVenta.UNIDAD, FormaVenta.PESO]


def test_una_tienda_sin_catalogo_no_ofrece_ninguna_forma(client, tienda_a):
    assert client.get(f"/api/t/{tienda_a.slug}/formas-de-venta").json() == []


def test_una_forma_sin_productos_publicados_no_aparece(
    client, tienda_a, crear_producto
):
    crear_producto(tienda_a, codigo="OCULTO", activo=False)

    assert client.get(f"/api/t/{tienda_a.slug}/formas-de-venta").json() == []


# ── Filtros ─────────────────────────────────────────────────────────────────


def test_el_listado_filtra_por_forma_de_venta(client, tienda_a, producto_a, granel_a):
    cuerpo = client.get(productos_de(tienda_a.slug), {"forma": FormaVenta.PESO}).json()

    assert [p["codigo"] for p in cuerpo["productos"]] == [granel_a.codigo]


def test_una_forma_que_no_existe_devuelve_vacio_y_no_un_error(
    client, tienda_a, producto_a
):
    """Viene de la URL: un enlace viejo no debería reventar la vitrina."""
    respuesta = client.get(productos_de(tienda_a.slug), {"forma": "inventada"})

    assert respuesta.status_code == 200
    assert respuesta.json()["productos"] == []


def test_el_listado_filtra_por_categoria(
    client, tienda_a, crear_categoria, crear_producto
):
    cocina = crear_categoria(tienda_a, nombre="cocina")
    crear_producto(tienda_a, codigo="CON-CAT", categoria=cocina)
    crear_producto(tienda_a, codigo="SIN-CAT")

    cuerpo = client.get(productos_de(tienda_a.slug), {"categoria": "cocina"}).json()

    assert [p["codigo"] for p in cuerpo["productos"]] == ["CON-CAT"]


def test_el_listado_pagina(client, tienda_a, crear_producto):
    for numero in range(14):
        crear_producto(tienda_a, codigo=f"P-{numero:02d}")

    primera = client.get(productos_de(tienda_a.slug)).json()
    segunda = client.get(productos_de(tienda_a.slug), {"pagina": 2}).json()

    assert primera["totalPaginas"] == 2
    assert len(primera["productos"]) == 12
    assert len(segunda["productos"]) == 2


# ── Cotizar ─────────────────────────────────────────────────────────────────


def test_cotizar_aplica_el_tramo_que_corresponde(client, tienda_a, crear_producto):
    from apps.precios.models import TramoPrecio, UnidadUmbral

    producto = crear_producto(tienda_a, codigo="VOL-1", precio_neto=4990)
    TramoPrecio.objects.create(
        tienda=tienda_a,
        producto=producto,
        unidad_umbral=UnidadUmbral.CANTIDAD,
        umbral=12,
        valor=4490,
    )

    cuerpo = cotizar(client, tienda_a.slug, "VOL-1", 12).json()

    assert cuerpo["precioUnitario"] == 4490
    assert cuerpo["tramoAplicado"] == 12
    assert cuerpo["neto"] == 53880


def test_cotizar_bajo_el_minimo_por_monto_responde_200_con_el_motivo(
    client, tienda_a, granel_a
):
    """
    Un rechazo no es un error de la petición.

    La cantidad es válida y la respuesta es «no se puede, por esto»: la vitrina
    necesita mostrar la razón donde corresponde, no una pantalla de error.
    """
    respuesta = cotizar(client, tienda_a.slug, granel_a.codigo, 10)

    assert respuesta.status_code == 200
    assert respuesta.json()["motivo"] == "bajo_minimo_por_monto"
    assert "20.000" in respuesta.json()["rechazo"]


def test_cotizar_sin_stock_lo_dice(client, tienda_a, producto_a):
    cuerpo = cotizar(client, tienda_a.slug, producto_a.codigo, 999).json()

    assert cuerpo["motivo"] == "sin_stock"


def test_cotizar_una_cantidad_invalida_si_es_400(client, tienda_a, producto_a):
    respuesta = cotizar(client, tienda_a.slug, producto_a.codigo, "muchos")

    assert respuesta.status_code == 400


def test_cotizar_el_producto_de_otra_tienda_responde_404(client, tienda_a, granel_b):
    respuesta = cotizar(client, tienda_a.slug, granel_b.codigo, 100)

    assert respuesta.status_code == 404


# ── Lo que no se muestra ────────────────────────────────────────────────────


def test_un_producto_desactivado_responde_404(client, tienda_a, crear_producto):
    crear_producto(tienda_a, codigo="OCULTO", activo=False)

    assert client.get(producto_de(tienda_a.slug, "OCULTO")).status_code == 404


def test_un_producto_agotado_responde_404(client, tienda_a, crear_producto):
    crear_producto(tienda_a, codigo="SIN-STOCK", stock=Decimal("0"))

    assert client.get(producto_de(tienda_a.slug, "SIN-STOCK")).status_code == 404


def test_una_tienda_inactiva_responde_404(client, tienda_a, producto_a):
    tienda_a.activa = False
    tienda_a.save(update_fields=["activa"])

    assert client.get(productos_de(tienda_a.slug)).status_code == 404


def test_una_tienda_que_no_existe_responde_404(client, db):
    assert client.get(productos_de("no-existe")).status_code == 404


def test_la_vitrina_no_pide_sesion(client, tienda_a, producto_a):
    assert client.get(productos_de(tienda_a.slug)).status_code == 200


# ── Aislamiento, desde la API ───────────────────────────────────────────────


@pytest.mark.aislamiento
def test_el_listado_de_una_tienda_no_trae_productos_de_la_otra(
    client, tienda_a, tienda_b, producto_a, producto_b
):
    de_a = client.get(productos_de(tienda_a.slug)).json()["productos"]
    de_b = client.get(productos_de(tienda_b.slug)).json()["productos"]

    assert [p["codigo"] for p in de_a] == [producto_a.codigo]
    assert [p["codigo"] for p in de_b] == [producto_b.codigo]


@pytest.mark.aislamiento
def test_pedir_el_producto_de_otra_tienda_por_su_codigo_responde_404(
    client, tienda_a, tienda_b, producto_a, producto_b
):
    """
    404 y no 403: un 403 confirmaría que ese código existe en alguna parte, y
    los códigos viajan en la URL.
    """
    assert client.get(producto_de(tienda_a.slug, producto_b.codigo)).status_code == 404
    assert client.get(producto_de(tienda_b.slug, producto_a.codigo)).status_code == 404


@pytest.mark.aislamiento
def test_el_filtro_por_forma_no_alcanza_la_otra_tienda(
    client, tienda_a, tienda_b, granel_a, granel_b
):
    de_a = client.get(
        productos_de(tienda_a.slug), {"forma": FormaVenta.PESO}
    ).json()["productos"]
    de_b = client.get(
        productos_de(tienda_b.slug), {"forma": FormaVenta.PESO}
    ).json()["productos"]

    assert [p["codigo"] for p in de_a] == [granel_a.codigo]
    assert [p["codigo"] for p in de_b] == [granel_b.codigo]


@pytest.mark.aislamiento
def test_las_formas_de_venta_son_las_de_cada_tienda(
    client, tienda_a, tienda_b, producto_a, granel_b
):
    de_a = client.get(f"/api/t/{tienda_a.slug}/formas-de-venta").json()
    de_b = client.get(f"/api/t/{tienda_b.slug}/formas-de-venta").json()

    assert [f["valor"] for f in de_a] == [FormaVenta.UNIDAD]
    assert [f["valor"] for f in de_b] == [FormaVenta.PESO]


@pytest.mark.aislamiento
def test_las_categorias_de_otra_tienda_no_se_filtran_por_la_composicion(
    client, tienda_a, tienda_b, lote_a, lote_b
):
    """
    La composición expone nombres de categoría: tienen que ser las propias.

    Es la fuga menos evidente del catálogo, porque el nombre de la categoría
    ajena viajaría dentro de un lote que sí es de esta tienda.
    """
    cuerpo = client.get(producto_de(tienda_a.slug, lote_a.codigo)).json()
    nombres = {c["categoria"] for c in cuerpo["composicion"]}

    ajenas = {c.categoria.nombre for c in lote_b.composicion.all()}
    assert not (nombres & ajenas)
