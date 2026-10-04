"""El comando que carga el catálogo de demostración de Joyas_ye."""

import pytest
from django.core.management import call_command

from apps.catalogo.models import Categoria, ComposicionLote, LineaGranel, Lote, TipoCupo
from apps.precios.models import TramoPrecio, UnidadUmbral
from apps.tiendas.models import Tienda

pytestmark = pytest.mark.django_db


@pytest.fixture
def cargar():
    def _cargar():
        call_command("cargar_demo", verbosity=0)
        return Tienda.objects.get(slug="joyas-ye")

    return _cargar


def test_crea_las_siete_categorias(cargar):
    tienda = cargar()

    assert Categoria.objects.de_tienda(tienda).count() == 7


def test_crea_las_cinco_lineas_de_granel(cargar):
    tienda = cargar()

    assert LineaGranel.objects.de_tienda(tienda).count() == 5


def test_crea_los_seis_lotes_de_ejemplo(cargar):
    tienda = cargar()

    lotes = Lote.objects.de_tienda(tienda)
    assert lotes.count() == 6
    assert {lote.codigo for lote in lotes} == {f"DEMO-0{n}" for n in range(1, 7)}


def test_todos_los_lotes_se_anuncian_como_ejemplo(cargar):
    """Nadie debe poder confundirlos con el catálogo real del cliente."""
    tienda = cargar()

    for lote in Lote.objects.de_tienda(tienda):
        assert "(ejemplo)" in lote.nombre


def test_la_composicion_de_cada_lote_cuadra(cargar):
    tienda = cargar()

    for lote in Lote.objects.de_tienda(tienda):
        suma = sum(c.cantidad for c in lote.composicion.all())
        assert suma == lote.cantidad_piezas, lote.codigo
        lote.full_clean()


def test_hay_lotes_de_cupo_unico_y_de_cupos_multiples(cargar):
    tienda = cargar()

    tipos = {lote.tipo_cupo for lote in Lote.objects.de_tienda(tienda)}
    assert tipos == {TipoCupo.UNICO, TipoCupo.MULTIPLE}


# ── Los precios del cliente, tal cual ───────────────────────────────────────


def test_los_tramos_del_granel_de_hombre_son_los_del_cliente(cargar):
    """Son precios reales: si esta prueba falla, alguien los "corrigió"."""
    tienda = cargar()
    linea = LineaGranel.objects.de_tienda(tienda).get(codigo="granel-hombre")

    tramos = {(t.unidad_umbral, int(t.umbral)): t.valor for t in linea.tramos.all()}

    assert tramos == {
        (UnidadUmbral.PESOS, 20000): 650,
        (UnidadUmbral.PESOS, 100000): 600,
        (UnidadUmbral.GRAMOS, 500): 560,
        (UnidadUmbral.GRAMOS, 1000): 500,
    }


def test_la_plata_colombiana_tiene_un_solo_tramo(cargar):
    tienda = cargar()
    linea = LineaGranel.objects.de_tienda(tienda).get(codigo="granel-plata-colombiana")

    assert linea.tramos.count() == 1
    assert linea.tramos.get().valor == 1800


def test_los_umbrales_en_gramos_van_como_gramos(cargar):
    """Medio kilo y kilo son gramos, no pesos. Confundirlos cambia el precio."""
    tienda = cargar()
    linea = LineaGranel.objects.de_tienda(tienda).get(codigo="granel-mujer")

    en_gramos = {int(t.umbral) for t in linea.tramos.filter(unidad_umbral="gramos")}
    assert en_gramos == {500, 1000}


def test_no_se_cargan_tramos_por_cantidad_de_lotes(cargar):
    """El cliente no los ha definido: inventarlos sería cobrar de más o de menos."""
    tienda = cargar()

    assert not TramoPrecio.objects.de_tienda(tienda).filter(linea_granel=None).exists()


# ── Idempotencia ────────────────────────────────────────────────────────────


def test_correrlo_dos_veces_no_duplica_nada(cargar):
    cargar()
    tienda = cargar()

    assert Categoria.objects.de_tienda(tienda).count() == 7
    assert LineaGranel.objects.de_tienda(tienda).count() == 5
    assert Lote.objects.de_tienda(tienda).count() == 6
    assert ComposicionLote.objects.de_tienda(tienda).count() == 13
    assert Tienda.objects.filter(slug="joyas-ye").count() == 1


def test_la_segunda_corrida_no_repone_los_cupos_vendidos(cargar):
    """Reponerlos borraría las ventas: un lote agotado volvería a ofrecerse."""
    tienda = cargar()
    lote = Lote.objects.de_tienda(tienda).get(codigo="DEMO-01")
    lote.cupos_disponibles = 2
    lote.save()

    cargar()

    lote.refresh_from_db()
    assert lote.cupos_disponibles == 2


def test_respeta_una_tienda_que_ya_existe(cargar):
    Tienda.objects.create(slug="joyas-ye", nombre="Joyas Ye de verdad")

    tienda = cargar()

    assert tienda.nombre == "Joyas Ye de verdad"


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_la_demostracion_no_toca_otra_tienda(cargar, tienda_b, crear_lote):
    """Cargar la demo de una tienda no puede alterar el catálogo de otra."""
    propio_de_b = crear_lote(tienda_b, codigo="B-001")

    cargar()

    assert list(Lote.objects.de_tienda(tienda_b)) == [propio_de_b]
    assert not LineaGranel.objects.de_tienda(tienda_b).exists()
