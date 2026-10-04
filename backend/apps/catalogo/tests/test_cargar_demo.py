"""
El comando que carga los catálogos de demostración.

Dos cosas se prueban acá y conviene no confundirlas: que los **precios del
cliente piloto quedan tal como los entregó** —si alguien los "ordena", esto
falla—, y que el comando se puede correr las veces que haga falta sin duplicar
ni reponer lo vendido.
"""

from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.catalogo.management.commands.cargar_demo import JOYAS_YE_GRANEL
from apps.catalogo.models import Categoria, ComposicionLote, FormaVenta, Producto
from apps.precios.models import TramoPrecio, UnidadUmbral
from apps.tiendas.models import Plan, Tienda

pytestmark = pytest.mark.django_db

PILOTO = "joyas-ye"
INVENTADA = "bazar-austral"


@pytest.fixture
def cargar():
    def _cargar(slug=PILOTO):
        call_command("cargar_demo", verbosity=0)
        return Tienda.objects.get(slug=slug)

    return _cargar


def productos_de(tienda, forma=None):
    productos = Producto.objects.de_tienda(tienda)
    return productos.filter(forma_venta=forma) if forma else productos


# ── Las dos tiendas ─────────────────────────────────────────────────────────


def test_carga_las_dos_tiendas(cargar):
    """
    Dos y no una: con una sola tienda, el aislamiento no se ve a mano.

    La segunda vende por unidad y lleva inventario, que es el caso que el
    cliente piloto no cubre.
    """
    cargar()

    assert Tienda.objects.filter(slug__in=[PILOTO, INVENTADA]).count() == 2


def test_el_piloto_vende_por_lote_y_por_peso(cargar):
    piloto = cargar()

    formas = set(productos_de(piloto).values_list("forma_venta", flat=True))
    assert formas == {FormaVenta.LOTE, FormaVenta.PESO}


def test_la_tienda_inventada_vende_por_unidad(cargar):
    bazar = cargar(INVENTADA)

    formas = set(productos_de(bazar).values_list("forma_venta", flat=True))
    assert formas == {FormaVenta.UNIDAD}


def test_el_piloto_queda_en_ultimate_para_mostrar_el_panel_entero(cargar):
    assert cargar().plan == Plan.ULTIMATE


def test_cada_tienda_tiene_su_paleta(cargar):
    cargar()

    piloto = Tienda.objects.get(slug=PILOTO)
    bazar = Tienda.objects.get(slug=INVENTADA)

    assert piloto.color_primario and bazar.color_primario
    assert piloto.color_primario != bazar.color_primario


# ── Catálogo del cliente piloto ─────────────────────────────────────────────


def test_crea_las_siete_categorias(cargar):
    assert Categoria.objects.de_tienda(cargar()).count() == 7


def test_crea_los_cinco_productos_por_peso(cargar):
    assert productos_de(cargar(), FormaVenta.PESO).count() == 5


def test_crea_los_seis_lotes_de_ejemplo(cargar):
    assert productos_de(cargar(), FormaVenta.LOTE).count() == 6


def test_todos_los_lotes_se_anuncian_como_ejemplo(cargar):
    """
    Son inventados y tienen que decirlo.

    Es una regla del proyecto: ningún dato sintético puede pasar por real.
    """
    lotes = productos_de(cargar(), FormaVenta.LOTE)

    assert all("(ejemplo)" in lote.nombre for lote in lotes)


def test_lo_que_se_vende_por_peso_no_controla_stock(cargar):
    """El cliente no registra gramos: lo que decide es el interruptor de activo."""
    for producto in productos_de(cargar(), FormaVenta.PESO):
        assert producto.controla_stock is False
        assert producto.stock is None


def test_los_lotes_controlan_stock(cargar):
    for lote in productos_de(cargar(), FormaVenta.LOTE):
        assert lote.controla_stock is True
        assert lote.stock > 0


def test_hay_lotes_que_se_venden_una_sola_vez(cargar):
    """Los cupos únicos de antes son productos con stock 1."""
    lotes = productos_de(cargar(), FormaVenta.LOTE)

    assert lotes.filter(stock=1).exists()
    assert lotes.filter(stock__gt=1).exists()


def test_la_composicion_de_cada_lote_cuadra(cargar):
    piloto = cargar()

    for lote in productos_de(piloto, FormaVenta.LOTE):
        piezas = sum(c.cantidad for c in lote.composicion.all())
        assert piezas == lote.cantidad_piezas


# ── Los precios del cliente, tal como los entregó ───────────────────────────


def test_el_precio_del_producto_es_el_de_su_primer_tramo(cargar):
    """
    El `precio_neto` es con lo que se arma el monto de referencia.

    En el cliente piloto es el precio de su primer tramo, tal como lo dio. Si
    alguien lo cambia por un promedio o por el precio más bajo, el mínimo de
    $20.000 deja de calzar con lo que él cobra.
    """
    piloto = cargar()

    for datos in JOYAS_YE_GRANEL:
        producto = Producto.objects.get(tienda=piloto, codigo=datos["codigo"])
        primer_tramo = min(
            producto.tramos.filter(unidad_umbral=UnidadUmbral.MONTO),
            key=lambda t: t.umbral,
        )
        assert producto.precio_neto == primer_tramo.valor


@pytest.mark.parametrize(
    ("codigo", "precio"),
    [
        ("granel-hombre", 650),
        ("granel-mujer", 900),
        ("granel-colgantes-aros-anillos", 1500),
        ("granel-plata-colombiana", 1800),
        ("granel-colgantes-hombre-xl", 1000),
    ],
)
def test_los_precios_base_son_los_que_dio_el_cliente(cargar, codigo, precio):
    """Escritos uno por uno: si alguien los redondea, esto falla por su nombre."""
    producto = Producto.objects.get(tienda=cargar(), codigo=codigo)

    assert producto.precio_neto == precio


def test_los_tramos_del_producto_de_hombre_son_los_del_cliente(cargar):
    producto = Producto.objects.get(tienda=cargar(), codigo="granel-hombre")

    tramos = {
        (t.unidad_umbral, int(t.umbral)): t.valor for t in producto.tramos.all()
    }

    assert tramos == {
        (UnidadUmbral.MONTO, 20000): 650,
        (UnidadUmbral.MONTO, 100000): 600,
        (UnidadUmbral.PESO, 500): 560,
        (UnidadUmbral.PESO, 1000): 500,
    }


def test_la_plata_colombiana_tiene_un_solo_tramo(cargar):
    producto = Producto.objects.get(tienda=cargar(), codigo="granel-plata-colombiana")

    assert producto.tramos.count() == 1
    assert producto.tramos.first().valor == 1800


def test_los_umbrales_de_medio_kilo_y_kilo_van_en_peso(cargar):
    """
    El cliente los expresó en gramos; los de pesos son montos.

    Son dos unidades distintas y el motor las usa en orden distinto: confundir
    una con otra cambia qué tramo se aplica.
    """
    producto = Producto.objects.get(tienda=cargar(), codigo="granel-mujer")
    por_peso = producto.tramos.filter(unidad_umbral=UnidadUmbral.PESO)

    assert {int(t.umbral) for t in por_peso} == {500, 1000}


def test_no_se_cargan_tramos_por_cantidad_de_lotes(cargar):
    """
    El cliente no los ha definido.

    Los cortes 1–2, 3–5 y 6 o más los propusimos nosotros, así que no pueden
    quedar cargados como si fueran suyos.
    """
    piloto = cargar()
    lotes = productos_de(piloto, FormaVenta.LOTE)

    assert not TramoPrecio.objects.filter(producto__in=lotes).exists()


# ── La tienda inventada ─────────────────────────────────────────────────────


def test_la_tienda_inventada_se_anuncia_como_ejemplo(cargar):
    for producto in productos_de(cargar(INVENTADA)):
        assert "(ejemplo)" in producto.nombre


def test_la_tienda_inventada_tiene_tramos_por_cantidad(cargar):
    """Es el caso que el piloto no cubre: precio unitario según cuántos lleves."""
    bazar = cargar(INVENTADA)
    tramos = TramoPrecio.objects.de_tienda(bazar)

    assert tramos.exists()
    assert set(tramos.values_list("unidad_umbral", flat=True)) == {
        UnidadUmbral.CANTIDAD
    }


def test_la_tienda_inventada_tiene_un_producto_con_la_ultima_unidad(cargar):
    """Para poder ver en pantalla el aviso de «queda una»."""
    assert productos_de(cargar(INVENTADA)).filter(stock=1).exists()


# ── Idempotencia ────────────────────────────────────────────────────────────


def test_correrlo_dos_veces_no_duplica_nada(cargar):
    cargar()
    productos = Producto.objects.count()
    tramos = TramoPrecio.objects.count()
    composiciones = ComposicionLote.objects.count()

    cargar()

    assert Producto.objects.count() == productos
    assert TramoPrecio.objects.count() == tramos
    assert ComposicionLote.objects.count() == composiciones


def test_la_segunda_corrida_no_repone_el_stock_vendido(cargar):
    """
    Volver a llenar el stock borraría las ventas y la demostración mentiría.
    """
    piloto = cargar()
    lote = productos_de(piloto, FormaVenta.LOTE).filter(stock__gt=1).first()
    lote.stock = Decimal("1")
    lote.save(update_fields=["stock"])

    cargar()

    lote.refresh_from_db()
    assert lote.stock == Decimal("1")


def test_respeta_una_tienda_que_ya_existe(cargar):
    tienda = Tienda.objects.create(slug=PILOTO, nombre="Joyas Ye")

    cargar()

    assert Tienda.objects.filter(slug=PILOTO).count() == 1
    assert Tienda.objects.get(pk=tienda.pk).plan == Plan.ULTIMATE


@pytest.mark.aislamiento
def test_la_demostracion_no_toca_otra_tienda(cargar, tienda_b, crear_producto):
    """Cargar la demostración no puede alterar el catálogo de un tercero."""
    ajeno = crear_producto(tienda_b, codigo="AJENO")

    cargar()

    ajeno.refresh_from_db()
    assert ajeno.nombre.startswith("Producto AJENO")
    assert productos_de(tienda_b).count() == 1
