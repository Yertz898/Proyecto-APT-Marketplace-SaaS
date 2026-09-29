"""
Endpoint público de la identidad de una tienda.

Es el primer endpoint del proyecto, así que trae la prueba de que pedir una
tienda que no corresponde responde 404 y no filtra nada de otra.
"""

import pytest

from apps.tiendas.models import Tienda

pytestmark = pytest.mark.django_db


def url_de(slug):
    return f"/api/t/{slug}/tienda"


def test_devuelve_la_identidad_de_la_tienda(client, tienda_a):
    respuesta = client.get(url_de(tienda_a.slug))

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "slug": "tienda-a",
        "nombre": "Tienda A",
        "logo": None,
        "banner": None,
        "colores": None,
        "redes": {"whatsapp": None, "instagram": None},
    }


def test_no_necesita_sesion(client, tienda_a):
    # La vitrina la ve cualquiera: es el único endpoint abierto.
    assert client.get(url_de(tienda_a.slug)).status_code == 200


def test_una_tienda_que_no_existe_responde_404(client, db):
    assert client.get(url_de("no-existe")).status_code == 404


def test_una_tienda_inactiva_responde_404(client, tienda_a):
    tienda_a.activa = False
    tienda_a.save()

    assert client.get(url_de(tienda_a.slug)).status_code == 404


def test_entrega_los_colores_solo_si_la_paleta_esta_completa(client, tienda_a):
    tienda_a.color_primario = "#7C3AED"
    tienda_a.color_acento = "#A78BFA"
    tienda_a.save()

    assert client.get(url_de(tienda_a.slug)).json()["colores"] is None

    tienda_a.color_primario_hover = "#8B5CF6"
    tienda_a.color_destacado = "#C9A227"
    tienda_a.save()

    colores = client.get(url_de(tienda_a.slug)).json()["colores"]
    assert colores == {
        "primario": "#7C3AED",
        "primarioHover": "#8B5CF6",
        "acento": "#A78BFA",
        "destacado": "#C9A227",
    }


def test_entrega_las_redes_cargadas(client, tienda_a):
    tienda_a.whatsapp = "https://wa.me/56912345678"
    tienda_a.save()

    redes = client.get(url_de(tienda_a.slug)).json()["redes"]

    assert redes == {"whatsapp": "https://wa.me/56912345678", "instagram": None}


@pytest.mark.aislamiento
def test_cada_slug_entrega_solo_su_tienda(client, tienda_a, tienda_b):
    tienda_a.whatsapp = "https://wa.me/56911111111"
    tienda_a.save()

    respuesta = client.get(url_de(tienda_b.slug)).json()

    assert respuesta["nombre"] == "Tienda B"
    assert respuesta["redes"]["whatsapp"] is None


@pytest.mark.aislamiento
def test_no_hay_forma_de_listar_todas_las_tiendas(client, tienda_a, tienda_b):
    # El endpoint es de detalle por slug: no existe un listado que exponga a
    # todos los comercios de la plataforma.
    assert Tienda.objects.count() == 2
    assert client.get("/api/t//tienda").status_code == 404
