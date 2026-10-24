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

from apps.catalogo.models import Categoria, ComposicionLote, Producto
from apps.precios.models import TramoPrecio

pytestmark = [pytest.mark.django_db, pytest.mark.aislamiento]


# ── Por tienda: el filtro explícito ─────────────────────────────────────────


def test_los_productos_de_una_tienda_no_incluyen_los_de_la_otra(
    tienda_a, tienda_b, producto_a, producto_b
):
    assert list(Producto.objects.de_tienda(tienda_a)) == [producto_a]
    assert list(Producto.objects.de_tienda(tienda_b)) == [producto_b]


def test_los_lotes_no_se_cruzan(tienda_a, tienda_b, lote_a, lote_b):
    assert list(Producto.objects.de_tienda(tienda_a)) == [lote_a]
    assert list(Producto.objects.de_tienda(tienda_b)) == [lote_b]


def test_los_productos_por_peso_no_se_cruzan(tienda_a, tienda_b, granel_a, granel_b):
    assert list(Producto.objects.de_tienda(tienda_a)) == [granel_a]
    assert list(Producto.objects.de_tienda(tienda_b)) == [granel_b]


def test_las_categorias_no_se_cruzan(tienda_a, tienda_b, crear_categoria):
    propia = crear_categoria(tienda_a, nombre="anillos")
    ajena = crear_categoria(tienda_b, nombre="aros")

    assert list(Categoria.objects.de_tienda(tienda_a)) == [propia]
    assert list(Categoria.objects.de_tienda(tienda_b)) == [ajena]


def test_las_composiciones_no_se_cruzan(tienda_a, tienda_b, lote_a, lote_b):
    de_a = ComposicionLote.objects.de_tienda(tienda_a)
    de_b = ComposicionLote.objects.de_tienda(tienda_b)

    assert {c.producto_id for c in de_a} == {lote_a.pk}
    assert {c.producto_id for c in de_b} == {lote_b.pk}


def test_los_tramos_de_precio_no_se_cruzan(tienda_a, tienda_b, granel_a, granel_b):
    de_a = TramoPrecio.objects.de_tienda(tienda_a)
    de_b = TramoPrecio.objects.de_tienda(tienda_b)

    assert {t.producto_id for t in de_a} == {granel_a.pk}
    assert {t.producto_id for t in de_b} == {granel_b.pk}


# ── Por usuario: lo que llega desde el token ────────────────────────────────


def test_el_dueno_de_una_tienda_solo_ve_los_productos_de_la_suya(
    dueno_a, vendedor_b, producto_a, producto_b
):
    assert list(Producto.objects.de_usuario(dueno_a)) == [producto_a]
    assert list(Producto.objects.de_usuario(vendedor_b)) == [producto_b]


def test_el_dueno_de_una_tienda_solo_ve_los_lotes_de_la_suya(
    dueno_a, vendedor_b, lote_a, lote_b
):
    assert list(Producto.objects.de_usuario(dueno_a)) == [lote_a]
    assert list(Producto.objects.de_usuario(vendedor_b)) == [lote_b]


def test_el_dueno_de_una_tienda_solo_ve_sus_tramos(
    dueno_a, vendedor_b, granel_a, granel_b
):
    de_a = TramoPrecio.objects.de_usuario(dueno_a)
    de_b = TramoPrecio.objects.de_usuario(vendedor_b)

    assert {t.producto_id for t in de_a} == {granel_a.pk}
    assert {t.producto_id for t in de_b} == {granel_b.pk}


def test_un_comprador_no_ve_el_catalogo_de_ninguna_tienda(
    comprador, producto_a, producto_b
):
    """Un comprador no trabaja en ninguna tienda: por el panel no ve nada."""
    assert not Producto.objects.de_usuario(comprador).exists()
    assert not TramoPrecio.objects.de_usuario(comprador).exists()


def test_el_anonimo_no_ve_el_catalogo_de_ninguna_tienda(producto_a, producto_b):
    from django.contrib.auth.models import AnonymousUser

    assert not Producto.objects.de_usuario(AnonymousUser()).exists()
    assert not Producto.objects.de_usuario(None).exists()


def test_el_administrador_de_plataforma_ve_las_dos_tiendas(
    admin_plataforma, producto_a, producto_b
):
    """Somos nosotros: es el único rol que cruza tiendas, y a propósito."""
    vistos = set(Producto.objects.de_usuario(admin_plataforma))

    assert vistos == {producto_a, producto_b}


# ── La vitrina pública ──────────────────────────────────────────────────────


def test_la_vitrina_de_una_tienda_no_muestra_productos_de_la_otra(
    tienda_a, tienda_b, producto_a, producto_b
):
    assert list(Producto.objects.publicadas_de(tienda_a)) == [producto_a]
    assert list(Producto.objects.publicadas_de(tienda_b)) == [producto_b]


def test_la_vitrina_de_una_tienda_no_muestra_los_lotes_de_la_otra(
    tienda_a, tienda_b, lote_a, lote_b
):
    assert list(Producto.objects.publicadas_de(tienda_a)) == [lote_a]
    assert list(Producto.objects.publicadas_de(tienda_b)) == [lote_b]


def test_la_vitrina_de_una_tienda_no_muestra_el_peso_de_la_otra(
    tienda_a, tienda_b, granel_a, granel_b
):
    assert list(Producto.objects.publicadas_de(tienda_a)) == [granel_a]
    assert list(Producto.objects.publicadas_de(tienda_b)) == [granel_b]


def test_buscar_por_codigo_no_alcanza_el_producto_de_la_otra_tienda(
    tienda_a, tienda_b, crear_producto
):
    """
    Conocer el código de un producto ajeno no sirve de nada.

    Es el caso que importa: el código viaja en la URL pública, así que es
    adivinable. El filtro por tienda tiene que ir antes que la búsqueda.
    """
    crear_producto(tienda_b, codigo="SECRETO-B")

    publicados_a = Producto.objects.publicadas_de(tienda_a)
    publicados_b = Producto.objects.publicadas_de(tienda_b)

    assert not publicados_a.filter(codigo="SECRETO-B").exists()
    assert publicados_b.filter(codigo="SECRETO-B").exists()


def test_filtrar_por_forma_de_venta_tampoco_cruza(
    tienda_a, tienda_b, lote_a, lote_b, crear_granel
):
    """El filtro de la vitrina se aplica *después* del de tienda, no antes."""
    from apps.catalogo.models import FormaVenta

    crear_granel(tienda_b, codigo="granel-solo-b")

    de_a = Producto.objects.publicadas_de(tienda_a).de_forma(FormaVenta.PESO)
    de_b = Producto.objects.publicadas_de(tienda_b).de_forma(FormaVenta.PESO)

    assert not de_a.exists()
    assert de_b.count() == 1


def test_filtrar_por_categoria_tampoco_cruza(
    tienda_a, tienda_b, crear_categoria, crear_producto
):
    """Dos tiendas pueden tener una categoría con el mismo nombre."""
    propia = crear_categoria(tienda_a, nombre="cocina")
    ajena = crear_categoria(tienda_b, nombre="cocina")
    crear_producto(tienda_a, codigo="A-COC", categoria=propia)
    crear_producto(tienda_b, codigo="B-COC", categoria=ajena)

    de_a = Producto.objects.publicadas_de(tienda_a).filter(categoria__nombre="cocina")
    de_b = Producto.objects.publicadas_de(tienda_b).filter(categoria__nombre="cocina")

    assert [p.codigo for p in de_a] == ["A-COC"]
    assert [p.codigo for p in de_b] == ["B-COC"]


# ── Escribir tampoco cruza ──────────────────────────────────────────────────


def test_un_tramo_no_puede_colgar_de_un_producto_de_otra_tienda(
    tienda_a, granel_b, codigos_de_error
):
    from django.core.exceptions import ValidationError

    from apps.precios.models import UnidadUmbral

    tramo = TramoPrecio(
        tienda=tienda_a,
        producto=granel_b,
        unidad_umbral=UnidadUmbral.MONTO,
        umbral=20000,
        valor=650,
    )

    with pytest.raises(ValidationError) as fallo:
        tramo.full_clean()

    assert "producto_de_otra_tienda" in codigos_de_error(fallo)


def test_una_composicion_no_puede_cruzar_tiendas(
    tienda_a, lote_a, tienda_b, crear_categoria, codigos_de_error
):
    from django.core.exceptions import ValidationError

    ajena = crear_categoria(tienda_b, nombre="de la otra")
    composicion = ComposicionLote(
        tienda=tienda_a, producto=lote_a, categoria=ajena, cantidad=1
    )

    with pytest.raises(ValidationError) as fallo:
        composicion.full_clean()

    assert "categoria_de_otra_tienda" in codigos_de_error(fallo)


def test_el_conteo_total_confirma_que_hay_datos_en_las_dos_tiendas(
    producto_a, producto_b
):
    """
    Guardia de las pruebas de arriba.

    Si las fixtures dejaran de crear datos en las dos tiendas, todas las
    pruebas de aislamiento pasarían sin probar nada.
    """
    assert Producto.objects.count() == 2
