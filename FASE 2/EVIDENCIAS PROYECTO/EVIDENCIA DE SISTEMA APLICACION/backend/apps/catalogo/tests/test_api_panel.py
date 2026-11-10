"""
El catálogo desde el panel.

Lo que distingue este listado del de la vitrina es que muestra lo que el
comprador no ve: lo desactivado y lo agotado, que es justamente lo que pide
atención.
"""

from decimal import Decimal

import pytest

pytestmark = pytest.mark.django_db

CATALOGO = "/api/panel/productos"
INVENTARIO = "/api/panel/inventario"


def como(client, usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


def codigos(respuesta):
    return [p["codigo"] for p in respuesta.json()["productos"]]


# ── Qué muestra ─────────────────────────────────────────────────────────────


def test_el_panel_muestra_lo_que_la_vitrina_esconde(
    client, dueno_a, tienda_a, crear_producto
):
    crear_producto(tienda_a, codigo="OCULTO", activo=False)
    crear_producto(tienda_a, codigo="AGOTADO", stock=Decimal("0"))

    assert set(codigos(como(client, dueno_a).get(CATALOGO))) == {"OCULTO", "AGOTADO"}


def test_cada_producto_trae_su_estado_en_una_palabra(
    client, dueno_a, tienda_a, crear_producto
):
    crear_producto(tienda_a, codigo="AGOTADO", stock=Decimal("0"))
    crear_producto(tienda_a, codigo="ULTIMA", stock=Decimal("1"))
    crear_producto(tienda_a, codigo="OCULTO", activo=False)
    crear_producto(tienda_a, codigo="NORMAL", stock=Decimal("20"))

    por_codigo = {
        p["codigo"]: p["estado"]
        for p in como(client, dueno_a).get(CATALOGO).json()["productos"]
    }

    assert por_codigo == {
        "AGOTADO": "agotado",
        "ULTIMA": "ultima",
        "OCULTO": "desactivado",
        "NORMAL": "publicado",
    }


def test_lo_que_no_lleva_inventario_no_tiene_stock(client, dueno_a, granel_a):
    producto = como(client, dueno_a).get(CATALOGO).json()["productos"][0]

    assert producto["controlaStock"] is False
    assert producto["stock"] is None
    assert producto["estado"] == "publicado"


def test_el_listado_dice_cuantos_tramos_tiene_cada_producto(
    client, dueno_a, granel_a, producto_a
):
    por_codigo = {
        p["codigo"]: p["tramos"]
        for p in como(client, dueno_a).get(CATALOGO).json()["productos"]
    }

    assert por_codigo[granel_a.codigo] == 1
    assert por_codigo[producto_a.codigo] == 0


def test_primero_aparece_lo_que_pide_atencion(
    client, dueno_a, tienda_a, crear_producto
):
    crear_producto(tienda_a, codigo="NORMAL", stock=Decimal("50"))
    crear_producto(tienda_a, codigo="AGOTADO", stock=Decimal("0"))
    crear_producto(tienda_a, codigo="OCULTO", activo=False)

    orden = codigos(como(client, dueno_a).get(CATALOGO))

    assert orden[0] == "OCULTO"
    assert orden.index("AGOTADO") < orden.index("NORMAL")


def test_el_listado_filtra_por_forma_de_venta(client, dueno_a, producto_a, granel_a):
    respuesta = como(client, dueno_a).get(CATALOGO, {"forma": "peso"})

    assert codigos(respuesta) == [granel_a.codigo]


# ── Inventario ──────────────────────────────────────────────────────────────


def test_el_inventario_cuenta_cada_situacion(client, dueno_a, tienda_a, crear_producto):
    crear_producto(tienda_a, codigo="NORMAL", stock=Decimal("50"))
    crear_producto(tienda_a, codigo="AGOTADO", stock=Decimal("0"))
    crear_producto(tienda_a, codigo="ULTIMA", stock=Decimal("1"))
    crear_producto(tienda_a, codigo="OCULTO", activo=False)

    cuerpo = como(client, dueno_a).get(INVENTARIO).json()

    assert cuerpo == {
        "publicados": 3,
        "desactivados": 1,
        "agotados": 1,
        "ultimaUnidad": 1,
    }


def test_lo_que_no_lleva_inventario_no_cuenta_como_agotado(client, dueno_a, granel_a):
    cuerpo = como(client, dueno_a).get(INVENTARIO).json()

    assert cuerpo["publicados"] == 1
    assert cuerpo["agotados"] == 0


# ── Quién entra ─────────────────────────────────────────────────────────────


def test_el_vendedor_ve_el_catalogo_de_su_tienda(client, vendedor_b, producto_b):
    assert codigos(como(client, vendedor_b).get(CATALOGO)) == [producto_b.codigo]


def test_un_comprador_no_entra_al_panel(client, comprador, producto_a):
    assert como(client, comprador).get(CATALOGO).status_code == 403


def test_sin_sesion_no_hay_panel(client, producto_a):
    assert client.get(CATALOGO).status_code == 401


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_el_panel_de_una_tienda_no_lista_productos_de_la_otra(
    client, dueno_a, vendedor_b, producto_a, producto_b
):
    de_a = codigos(como(client, dueno_a).get(CATALOGO))
    de_b = codigos(como(client, vendedor_b).get(CATALOGO))

    assert de_a == [producto_a.codigo]
    assert de_b == [producto_b.codigo]


@pytest.mark.aislamiento
def test_el_panel_muestra_hasta_lo_desactivado_pero_nunca_lo_ajeno(
    client, dueno_a, tienda_a, tienda_b, crear_producto
):
    """
    El caso que importa: el panel sí muestra lo oculto de su tienda.

    Es el listado con menos filtros del sistema, así que es donde una fuga
    pasaría más desapercibida.
    """
    crear_producto(tienda_a, codigo="PROPIO", activo=False)
    crear_producto(tienda_b, codigo="AJENO", activo=False)

    assert codigos(como(client, dueno_a).get(CATALOGO)) == ["PROPIO"]


@pytest.mark.aislamiento
def test_el_inventario_cuenta_solo_la_tienda_propia(
    client, dueno_a, vendedor_b, tienda_a, tienda_b, crear_producto
):
    crear_producto(tienda_a, codigo="A-1")
    crear_producto(tienda_b, codigo="B-1")
    crear_producto(tienda_b, codigo="B-2")

    de_a = como(client, dueno_a).get(INVENTARIO).json()
    de_b = como(client, vendedor_b).get(INVENTARIO).json()

    assert de_a["publicados"] == 1
    assert de_b["publicados"] == 2
