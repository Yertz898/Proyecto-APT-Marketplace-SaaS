"""
El motor de precios.

Es la parte del sistema que más fácil se calcula mal, así que las pruebas van
en dos capas: **la matriz genérica de la plataforma** —un producto de cada
forma de venta— y después **los casos del cliente piloto con sus precios
reales**, que son el contraste contra la realidad.

La regla está en CONVENCIONES.md > Tramos de precio.
"""

from decimal import Decimal

import pytest

from apps.catalogo.models import FormaVenta, Producto, UnidadMedida
from apps.precios.models import TramoPrecio, UnidadUmbral
from apps.precios.servicios import MotivoRechazo, cotizar

pytestmark = pytest.mark.django_db


@pytest.fixture
def con_tramos(db):
    """Un producto y sus tramos, descritos como (unidad, umbral, precio)."""

    def _crear(tienda, tramos, **extra):
        datos = {
            "tienda": tienda,
            "codigo": extra.pop("codigo", "T-1"),
            "nombre": "Producto",
            "precio_neto": extra.pop("precio_neto", 1000),
            "forma_venta": FormaVenta.UNIDAD,
            "unidad_medida": UnidadMedida.UNIDAD,
            "controla_stock": False,
            "stock": None,
        }
        datos.update(extra)
        producto = Producto.objects.create(**datos)

        for unidad, umbral, valor in tramos:
            TramoPrecio.objects.create(
                tienda=tienda,
                producto=producto,
                unidad_umbral=unidad,
                umbral=Decimal(umbral),
                valor=valor,
            )
        return producto

    return _crear


# ── Sin tramos ──────────────────────────────────────────────────────────────


def test_sin_tramos_se_cobra_el_precio_del_producto(tienda_a, con_tramos):
    producto = con_tramos(tienda_a, [], precio_neto=4990)

    resultado = cotizar(producto, Decimal("3"))

    assert resultado.precio_unitario == 4990
    assert resultado.neto == 14970
    assert resultado.tramo_aplicado is None


def test_el_iva_y_el_total_vienen_calculados(tienda_a, con_tramos):
    producto = con_tramos(tienda_a, [], precio_neto=10000)

    resultado = cotizar(producto, Decimal("1"))

    assert (resultado.neto, resultado.iva, resultado.total) == (10000, 1900, 11900)


def test_el_iva_redondea_medio_hacia_arriba(tienda_a, con_tramos):
    """
    El `round()` de Python redondea al par y deja el total un peso corto.

    Con un neto de 20.150 el IVA exacto es 3.828,50: tiene que quedar 3.829.
    """
    producto = con_tramos(tienda_a, [], precio_neto=20150)

    assert cotizar(producto, Decimal("1")).iva == 3829


# ── Matriz genérica: una forma de venta por caso ────────────────────────────


def test_por_unidad_aplica_el_tramo_por_cantidad(tienda_a, con_tramos):
    producto = con_tramos(
        tienda_a,
        [(UnidadUmbral.CANTIDAD, 12, 4490), (UnidadUmbral.CANTIDAD, 48, 3990)],
        precio_neto=4990,
    )

    assert cotizar(producto, Decimal("11")).precio_unitario == 4990
    assert cotizar(producto, Decimal("12")).precio_unitario == 4490
    assert cotizar(producto, Decimal("48")).precio_unitario == 3990


def test_los_umbrales_son_inclusivos(tienda_a, con_tramos):
    """«Desde 12» incluye los 12 exactos. Confirmado con el cliente."""
    producto = con_tramos(tienda_a, [(UnidadUmbral.CANTIDAD, 12, 4490)])

    assert cotizar(producto, Decimal("12")).tramo_aplicado == 12


def test_por_lote_el_stock_limita_la_cantidad(tienda_a, crear_lote):
    lote = crear_lote(tienda_a)

    assert cotizar(lote, Decimal("3")).aceptada
    assert cotizar(lote, Decimal("4")).motivo == MotivoRechazo.SIN_STOCK


def test_un_lote_que_se_vende_una_sola_vez_admite_uno(tienda_a, crear_lote):
    unico = crear_lote(tienda_a, codigo="UNICO", stock=Decimal("1"))

    assert cotizar(unico, Decimal("1")).aceptada
    assert not cotizar(unico, Decimal("2")).aceptada


def test_por_peso_los_umbrales_en_peso_tienen_prioridad(tienda_a, con_tramos):
    """
    Con 1.000 g se aplica el tramo de peso, no el de monto.

    Es la regla que ordena el motor: lo pedido en peso o en cantidad se mira
    primero, y el monto es el camino de respaldo.
    """
    producto = con_tramos(
        tienda_a,
        [(UnidadUmbral.MONTO, 20000, 650), (UnidadUmbral.PESO, 1000, 500)],
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.GRAMO,
        precio_neto=650,
    )

    resultado = cotizar(producto, Decimal("1000"))

    assert resultado.precio_unitario == 500
    assert resultado.unidad_tramo == UnidadUmbral.PESO


def test_por_peso_sin_alcanzar_el_peso_se_usa_el_monto(tienda_a, con_tramos):
    producto = con_tramos(
        tienda_a,
        [(UnidadUmbral.MONTO, 20000, 650), (UnidadUmbral.PESO, 1000, 500)],
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.GRAMO,
        precio_neto=650,
    )

    resultado = cotizar(producto, Decimal("100"))

    assert resultado.precio_unitario == 650
    assert resultado.unidad_tramo == UnidadUmbral.MONTO


def test_el_peso_admite_decimales(tienda_a, con_tramos):
    producto = con_tramos(
        tienda_a,
        [(UnidadUmbral.MONTO, 20000, 650)],
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.GRAMO,
        precio_neto=650,
    )

    assert cotizar(producto, Decimal("100.5")).neto == 65325


# ── Los dos rechazos, que no son lo mismo ───────────────────────────────────


def test_bajo_el_primer_tramo_por_monto_se_rechaza(tienda_a, con_tramos):
    producto = con_tramos(
        tienda_a, [(UnidadUmbral.MONTO, 20000, 650)], precio_neto=650
    )

    resultado = cotizar(producto, Decimal("10"))

    assert resultado.motivo == MotivoRechazo.BAJO_MINIMO_POR_MONTO
    assert "20.000" in resultado.rechazo


def test_el_monto_de_referencia_sale_del_precio_del_producto(tienda_a, con_tramos):
    """
    No del tramo más barato ni de un promedio.

    Con precio 650, llegar a $20.000 pide 31 gramos (30 quedan en 19.500).
    """
    producto = con_tramos(
        tienda_a,
        [(UnidadUmbral.MONTO, 20000, 650)],
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.GRAMO,
        precio_neto=650,
    )

    assert not cotizar(producto, Decimal("30")).aceptada
    assert cotizar(producto, Decimal("31")).aceptada


def test_bajo_la_cantidad_minima_se_rechaza_por_otra_razon(tienda_a, con_tramos):
    """
    La cantidad mínima no es el mínimo por monto.

    Son dos rechazos distintos, con mensajes distintos, y confundirlos deja al
    comprador sin saber qué corregir.
    """
    producto = con_tramos(tienda_a, [], cantidad_minima=Decimal("5"))

    resultado = cotizar(producto, Decimal("2"))

    assert resultado.motivo == MotivoRechazo.BAJO_CANTIDAD_MINIMA
    assert "mínima" in resultado.rechazo


def test_la_cantidad_minima_se_mira_antes_que_el_stock(tienda_a, con_tramos):
    producto = con_tramos(
        tienda_a,
        [],
        cantidad_minima=Decimal("5"),
        controla_stock=True,
        stock=Decimal("0"),
    )

    assert cotizar(producto, Decimal("1")).motivo == MotivoRechazo.BAJO_CANTIDAD_MINIMA


def test_un_rechazo_no_trae_precio(tienda_a, con_tramos):
    producto = con_tramos(tienda_a, [], cantidad_minima=Decimal("5"))

    resultado = cotizar(producto, Decimal("1"))

    assert (resultado.neto, resultado.iva, resultado.total) == (0, 0, 0)


def test_sin_tramos_por_monto_no_hay_minimo_que_rechazar(tienda_a, con_tramos):
    producto = con_tramos(tienda_a, [(UnidadUmbral.CANTIDAD, 12, 4490)])

    assert cotizar(producto, Decimal("1")).aceptada


# ── Aviso de conveniencia ───────────────────────────────────────────────────


def test_avisa_cuando_llevar_mas_sale_mas_barato(tienda_a, con_tramos):
    """
    Pasa de verdad con los precios del cliente piloto.

    Se avisa y no se cambia la cantidad por el comprador: la decisión es suya.
    """
    producto = con_tramos(
        tienda_a,
        [(UnidadUmbral.MONTO, 20000, 650), (UnidadUmbral.PESO, 1000, 500)],
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.GRAMO,
        precio_neto=650,
    )

    resultado = cotizar(producto, Decimal("900"))

    assert resultado.aviso is not None
    assert "1000 g" in resultado.aviso


def test_no_avisa_cuando_llevar_mas_sale_mas_caro(tienda_a, con_tramos):
    producto = con_tramos(
        tienda_a,
        [(UnidadUmbral.MONTO, 20000, 650), (UnidadUmbral.PESO, 1000, 500)],
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.GRAMO,
        precio_neto=650,
    )

    assert cotizar(producto, Decimal("500")).aviso is None


# ── Los casos del cliente piloto, con sus precios reales ────────────────────


@pytest.fixture
def piloto(db):
    """La tienda del cliente, cargada con el comando de demostración."""
    from django.core.management import call_command

    call_command("cargar_demo", verbosity=0)
    from apps.tiendas.models import Tienda

    return Tienda.objects.get(slug="joyas-ye")


def producto_del_piloto(piloto, codigo):
    return Producto.objects.get(tienda=piloto, codigo=codigo)


@pytest.mark.parametrize(
    ("codigo", "gramos", "precio_unitario"),
    [
        # Línea de hombre: 650 base, 600 sobre $100.000, 560 desde medio kilo,
        # 500 desde el kilo.
        ("granel-hombre", 100, 650),
        ("granel-hombre", 200, 600),
        ("granel-hombre", 500, 560),
        ("granel-hombre", 1000, 500),
        # Línea de mujer: 900 / 850 / 780 / 700.
        ("granel-mujer", 100, 900),
        ("granel-mujer", 500, 780),
        ("granel-mujer", 1000, 700),
        # Un solo tramo: siempre el mismo precio.
        ("granel-plata-colombiana", 100, 1800),
        ("granel-colgantes-hombre-xl", 100, 1000),
    ],
)
def test_los_precios_del_piloto_calzan_con_su_lista(
    piloto, codigo, gramos, precio_unitario
):
    producto = producto_del_piloto(piloto, codigo)

    resultado = cotizar(producto, Decimal(gramos))

    assert resultado.aceptada
    assert resultado.precio_unitario == precio_unitario


def test_el_minimo_de_veinte_mil_del_piloto(piloto):
    """
    Los $20.000 salen del primer tramo por monto, no de la cantidad mínima.

    Con 650 el gramo, 30 gramos son $19.500 y no alcanzan; 31 son $20.150.
    """
    hombre = producto_del_piloto(piloto, "granel-hombre")

    assert cotizar(hombre, Decimal("30")).motivo == MotivoRechazo.BAJO_MINIMO_POR_MONTO
    assert cotizar(hombre, Decimal("31")).aceptada


def test_los_veinte_mil_exactos_entran(piloto):
    """«Sobre 20 mil» incluye los $20.000 exactos. Confirmado el 27-09-2026."""
    colgantes = producto_del_piloto(piloto, "granel-colgantes-hombre-xl")

    # A 1.000 el gramo, 20 gramos son exactamente $20.000.
    resultado = cotizar(colgantes, Decimal("20"))

    assert resultado.aceptada
    assert resultado.neto == 20000
    assert resultado.iva == 3800
    assert resultado.total == 23800


def test_el_kilo_de_la_linea_de_hombre(piloto):
    hombre = producto_del_piloto(piloto, "granel-hombre")

    resultado = cotizar(hombre, Decimal("1000"))

    assert resultado.neto == 500000
    assert resultado.total == 595000


def test_entre_novecientos_y_el_kilo_conviene_el_kilo(piloto):
    """El caso que motivó el aviso de conveniencia."""
    hombre = producto_del_piloto(piloto, "granel-hombre")

    novecientos = cotizar(hombre, Decimal("900"))

    assert novecientos.neto > cotizar(hombre, Decimal("1000")).neto
    assert novecientos.aviso is not None


def test_un_lote_del_piloto_se_cobra_a_su_precio(piloto):
    """Sus lotes no tienen tramos: el cliente no los ha definido."""
    lote = producto_del_piloto(piloto, "DEMO-01")

    resultado = cotizar(lote, Decimal("2"))

    assert resultado.precio_unitario == 45990
    assert resultado.tramo_aplicado is None
