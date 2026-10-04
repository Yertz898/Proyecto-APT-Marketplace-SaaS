"""
Aislamiento del catálogo entre tiendas.

Es el invariante del sistema: la aplicación aloja varios comercios sobre una
misma base de datos, y una omisión acá no produce un error visible sino una
filtración silenciosa de datos comerciales de terceros.

Cada prueba va en los **dos sentidos**: que la tienda A no alcanza lo de la B
y que la B no alcanza lo de la A. Una sola dirección deja pasar un filtro
escrito al revés.

Para el checklist del proyecto:

    docker compose exec api pytest -m aislamiento
"""

import pytest

from apps.catalogo.models import Categoria, ComposicionLote, LineaGranel, Lote
from apps.precios.models import TramoPrecio

pytestmark = [pytest.mark.django_db, pytest.mark.aislamiento]


# ── Por tienda: el filtro explícito ─────────────────────────────────────────


def test_los_lotes_de_una_tienda_no_incluyen_los_de_la_otra(
    tienda_a, tienda_b, lote_a, lote_b
):
    de_a = Lote.objects.de_tienda(tienda_a)
    de_b = Lote.objects.de_tienda(tienda_b)

    assert list(de_a) == [lote_a]
    assert list(de_b) == [lote_b]


def test_las_lineas_de_granel_no_se_cruzan(tienda_a, tienda_b, granel_a, granel_b):
    assert list(LineaGranel.objects.de_tienda(tienda_a)) == [granel_a]
    assert list(LineaGranel.objects.de_tienda(tienda_b)) == [granel_b]


def test_las_categorias_no_se_cruzan(tienda_a, tienda_b, crear_categoria):
    propia = crear_categoria(tienda_a, nombre="anillos")
    ajena = crear_categoria(tienda_b, nombre="aros")

    assert list(Categoria.objects.de_tienda(tienda_a)) == [propia]
    assert list(Categoria.objects.de_tienda(tienda_b)) == [ajena]


def test_las_composiciones_no_se_cruzan(tienda_a, tienda_b, lote_a, lote_b):
    de_a = ComposicionLote.objects.de_tienda(tienda_a)
    de_b = ComposicionLote.objects.de_tienda(tienda_b)

    assert {c.lote_id for c in de_a} == {lote_a.pk}
    assert {c.lote_id for c in de_b} == {lote_b.pk}


def test_los_tramos_de_precio_no_se_cruzan(tienda_a, tienda_b, granel_a, granel_b):
    de_a = TramoPrecio.objects.de_tienda(tienda_a)
    de_b = TramoPrecio.objects.de_tienda(tienda_b)

    assert {t.linea_granel_id for t in de_a} == {granel_a.pk}
    assert {t.linea_granel_id for t in de_b} == {granel_b.pk}


# ── Por usuario: lo que llega desde el token ────────────────────────────────


def test_el_dueno_de_una_tienda_solo_ve_los_lotes_de_la_suya(
    dueno_a, vendedor_b, lote_a, lote_b
):
    assert list(Lote.objects.de_usuario(dueno_a)) == [lote_a]
    assert list(Lote.objects.de_usuario(vendedor_b)) == [lote_b]


def test_el_dueno_de_una_tienda_solo_ve_el_granel_de_la_suya(
    dueno_a, vendedor_b, granel_a, granel_b
):
    assert list(LineaGranel.objects.de_usuario(dueno_a)) == [granel_a]
    assert list(LineaGranel.objects.de_usuario(vendedor_b)) == [granel_b]


def test_un_comprador_no_ve_el_catalogo_de_ninguna_tienda(comprador, lote_a, lote_b):
    """Un comprador no trabaja en ninguna tienda: por el panel no ve nada."""
    assert not Lote.objects.de_usuario(comprador).exists()
    assert not LineaGranel.objects.de_usuario(comprador).exists()


def test_el_anonimo_no_ve_el_catalogo_de_ninguna_tienda(lote_a, lote_b):
    from django.contrib.auth.models import AnonymousUser

    assert not Lote.objects.de_usuario(AnonymousUser()).exists()
    assert not Lote.objects.de_usuario(None).exists()


def test_el_administrador_de_plataforma_ve_las_dos_tiendas(
    admin_plataforma, lote_a, lote_b
):
    """Somos nosotros: es el único rol que cruza tiendas, y a propósito."""
    vistos = set(Lote.objects.de_usuario(admin_plataforma))

    assert vistos == {lote_a, lote_b}


# ── La vitrina pública ──────────────────────────────────────────────────────


def test_la_vitrina_de_una_tienda_no_muestra_lotes_de_la_otra(
    tienda_a, tienda_b, lote_a, lote_b
):
    assert list(Lote.objects.publicadas_de(tienda_a)) == [lote_a]
    assert list(Lote.objects.publicadas_de(tienda_b)) == [lote_b]


def test_la_vitrina_de_una_tienda_no_muestra_granel_de_la_otra(
    tienda_a, tienda_b, granel_a, granel_b
):
    assert list(LineaGranel.objects.publicadas_de(tienda_a)) == [granel_a]
    assert list(LineaGranel.objects.publicadas_de(tienda_b)) == [granel_b]


def test_buscar_por_codigo_no_alcanza_el_lote_de_la_otra_tienda(
    tienda_a, tienda_b, crear_lote
):
    """
    Conocer el código de un lote ajeno no sirve de nada.

    Es el caso que importa: el código viaja en la URL pública, así que es
    adivinable. El filtro por tienda tiene que ir antes que la búsqueda.
    """
    crear_lote(tienda_b, codigo="SECRETO-B")

    assert not Lote.objects.publicadas_de(tienda_a).filter(codigo="SECRETO-B").exists()
    assert Lote.objects.publicadas_de(tienda_b).filter(codigo="SECRETO-B").exists()


def test_buscar_por_codigo_no_alcanza_el_granel_de_la_otra_tienda(
    tienda_a, tienda_b, crear_granel
):
    crear_granel(tienda_b, codigo="granel-secreto-b")

    assert not (
        LineaGranel.objects.publicadas_de(tienda_a)
        .filter(codigo="granel-secreto-b")
        .exists()
    )
    assert (
        LineaGranel.objects.publicadas_de(tienda_b)
        .filter(codigo="granel-secreto-b")
        .exists()
    )


# ── Escribir tampoco cruza ──────────────────────────────────────────────────


def test_un_tramo_no_puede_colgar_de_una_linea_de_otra_tienda(
    tienda_a, granel_b, codigos_de_error
):
    from django.core.exceptions import ValidationError

    from apps.precios.models import UnidadUmbral

    tramo = TramoPrecio(
        tienda=tienda_a,
        linea_granel=granel_b,
        unidad_umbral=UnidadUmbral.PESOS,
        umbral=20000,
        precio_unitario_neto=650,
    )

    with pytest.raises(ValidationError) as fallo:
        tramo.full_clean()

    assert "linea_de_otra_tienda" in codigos_de_error(fallo)


def test_el_conteo_total_confirma_que_hay_datos_en_las_dos_tiendas(lote_a, lote_b):
    """
    Guardia de las pruebas de arriba.

    Si las fixtures dejaran de crear datos en las dos tiendas, todas las
    pruebas de aislamiento pasarían sin probar nada.
    """
    assert Lote.objects.count() == 2
