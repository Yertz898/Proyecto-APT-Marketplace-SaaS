"""
API pública del catálogo.

La forma de estas respuestas la fija el frontend, que ya está escrito. Si una
clave cambia de nombre acá, la vitrina deja de mostrar el dato sin que nada
falle a gritos: por eso las pruebas afirman sobre el conjunto exacto de claves.
"""

import pytest

pytestmark = pytest.mark.django_db


def lotes_de(slug):
    return f"/api/t/{slug}/lotes"


def granel_de(slug):
    return f"/api/t/{slug}/granel"


# ── Forma de la respuesta ───────────────────────────────────────────────────


def test_el_listado_trae_la_forma_que_espera_la_vitrina(client, tienda_a, lote_a):
    cuerpo = client.get(lotes_de(tienda_a.slug)).json()

    assert set(cuerpo) == {"lotes", "paginaActual", "totalPaginas"}
    assert set(cuerpo["lotes"][0]) == {
        "tipo",
        "codigo",
        "nombre",
        "material",
        "piezasTotales",
        "composicion",
        "precioNeto",
        "iva",
        "precioTotal",
        "cupos",
        "agotado",
        "foto",
    }


def test_el_lote_trae_el_iva_y_el_total_calculados(client, tienda_a, crear_lote):
    """El navegador no hace aritmética de dinero: la hace el backend."""
    crear_lote(tienda_a, codigo="IVA-01", precio_neto=45990)

    lote = client.get(f"{lotes_de(tienda_a.slug)}/IVA-01").json()

    assert lote["precioNeto"] == 45990
    assert lote["iva"] == 8738
    assert lote["precioTotal"] == 54728


def test_un_lote_de_cupo_unico_no_dice_cuantos_quedan(client, tienda_a, crear_lote):
    crear_lote(
        tienda_a,
        codigo="UNICO-01",
        tipo_cupo="UNICO",
        cupos_totales=1,
        cupos_disponibles=1,
    )

    lote = client.get(f"{lotes_de(tienda_a.slug)}/UNICO-01").json()

    assert lote["cupos"] == {"tipo": "UNICO"}


def test_un_lote_de_cupos_multiples_dice_cuantos_quedan(client, tienda_a, lote_a):
    lote = client.get(f"{lotes_de(tienda_a.slug)}/{lote_a.codigo}").json()

    assert lote["cupos"] == {"tipo": "MULTIPLE", "restantes": 3}


def test_un_lote_sin_foto_devuelve_null(client, tienda_a, lote_a):
    """Null y no un marcador: la interfaz no dibuja nada en su lugar."""
    lote = client.get(f"{lotes_de(tienda_a.slug)}/{lote_a.codigo}").json()

    assert lote["foto"] is None


def test_la_linea_de_granel_trae_la_forma_que_espera_la_vitrina(
    client, tienda_a, granel_a
):
    cuerpo = client.get(granel_de(tienda_a.slug)).json()

    assert set(cuerpo[0]) == {
        "tipo",
        "codigo",
        "nombre",
        "material",
        "categorias",
        "tramos",
        "minimo",
    }
    assert set(cuerpo[0]["tramos"][0]) == {"umbral", "unidadUmbral", "precioGramoNeto"}


def test_el_minimo_lo_redacta_el_backend(client, tienda_a, granel_a):
    linea = client.get(f"{granel_de(tienda_a.slug)}/{granel_a.codigo}").json()

    assert linea["minimo"] == "Compra mínima de $20.000"


# ── Paginación ──────────────────────────────────────────────────────────────


def test_el_listado_pagina(client, tienda_a, crear_lote):
    for n in range(15):
        crear_lote(tienda_a, codigo=f"P-{n:02d}")

    primera = client.get(lotes_de(tienda_a.slug), {"pagina": 1}).json()
    segunda = client.get(lotes_de(tienda_a.slug), {"pagina": 2}).json()

    assert primera["totalPaginas"] == 2
    assert len(primera["lotes"]) == 12
    assert len(segunda["lotes"]) == 3
    assert segunda["paginaActual"] == 2


# ── Lo que no se muestra ────────────────────────────────────────────────────


def test_un_lote_desactivado_responde_404(client, tienda_a, crear_lote):
    crear_lote(tienda_a, codigo="APAGADO", activo=False)

    assert client.get(f"{lotes_de(tienda_a.slug)}/APAGADO").status_code == 404


def test_un_lote_agotado_responde_404(client, tienda_a, crear_lote):
    crear_lote(tienda_a, codigo="AGOTADO", cupos_totales=2, cupos_disponibles=0)

    assert client.get(f"{lotes_de(tienda_a.slug)}/AGOTADO").status_code == 404


def test_una_linea_de_granel_no_disponible_responde_404(client, tienda_a, crear_granel):
    crear_granel(tienda_a, codigo="apagada", disponible=False)

    assert client.get(f"{granel_de(tienda_a.slug)}/apagada").status_code == 404


def test_una_tienda_inactiva_responde_404(client, tienda_a, lote_a):
    tienda_a.activa = False
    tienda_a.save()

    assert client.get(lotes_de(tienda_a.slug)).status_code == 404


def test_una_tienda_que_no_existe_responde_404(client, db):
    assert client.get(lotes_de("no-existe")).status_code == 404


def test_la_vitrina_no_pide_sesion(client, tienda_a, lote_a):
    assert client.get(lotes_de(tienda_a.slug)).status_code == 200


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_el_listado_de_una_tienda_no_trae_lotes_de_la_otra(
    client, tienda_a, tienda_b, lote_a, lote_b
):
    de_a = client.get(lotes_de(tienda_a.slug)).json()["lotes"]
    de_b = client.get(lotes_de(tienda_b.slug)).json()["lotes"]

    assert [lote["codigo"] for lote in de_a] == [lote_a.codigo]
    assert [lote["codigo"] for lote in de_b] == [lote_b.codigo]


@pytest.mark.aislamiento
def test_pedir_el_lote_de_otra_tienda_por_su_codigo_responde_404(
    client, tienda_a, tienda_b, lote_b
):
    """
    El código viaja en la URL pública, así que es adivinable.

    404 y no 403: un 403 confirmaría que ese lote existe en otra tienda.
    """
    respuesta = client.get(f"{lotes_de(tienda_a.slug)}/{lote_b.codigo}")

    assert respuesta.status_code == 404
    assert client.get(f"{lotes_de(tienda_b.slug)}/{lote_b.codigo}").status_code == 200


@pytest.mark.aislamiento
def test_el_granel_de_una_tienda_no_aparece_en_la_otra(
    client, tienda_a, tienda_b, granel_a, granel_b
):
    de_a = client.get(granel_de(tienda_a.slug)).json()
    de_b = client.get(granel_de(tienda_b.slug)).json()

    assert [linea["codigo"] for linea in de_a] == [granel_a.codigo]
    assert [linea["codigo"] for linea in de_b] == [granel_b.codigo]


@pytest.mark.aislamiento
def test_pedir_el_granel_de_otra_tienda_por_su_codigo_responde_404(
    client, tienda_a, tienda_b, granel_b
):
    respuesta = client.get(f"{granel_de(tienda_a.slug)}/{granel_b.codigo}")

    assert respuesta.status_code == 404
    assert (
        client.get(f"{granel_de(tienda_b.slug)}/{granel_b.codigo}").status_code == 200
    )


@pytest.mark.aislamiento
def test_las_categorias_de_otra_tienda_no_se_filtran_por_la_composicion(
    client, tienda_a, tienda_b, lote_a, lote_b
):
    """El nombre de una categoría ajena no debe asomar en la vitrina propia."""
    categorias_de_b = {
        c.categoria.nombre for c in lote_b.composicion.select_related("categoria")
    }

    cuerpo = client.get(lotes_de(tienda_a.slug)).json()
    vistas = {
        pieza["categoria"] for lote in cuerpo["lotes"] for pieza in lote["composicion"]
    }

    assert not vistas & categorias_de_b
