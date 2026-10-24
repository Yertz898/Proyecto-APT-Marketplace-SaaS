"""Restricciones y validaciones del catálogo.

Lo que se prueba acá es que la base de datos sostiene las reglas por su cuenta.
Una validación que solo vive en un formulario se salta desde el admin, desde
una carga masiva o desde una vista nueva mal escrita.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.catalogo.models import (
    Categoria,
    ComposicionLote,
    FormaVenta,
    Producto,
    UnidadMedida,
)

pytestmark = pytest.mark.django_db


def producto(tienda, **extra):
    """Un producto mínimo y válido, para variarle un campo por prueba."""
    datos = {
        "tienda": tienda,
        "codigo": "X-1",
        "nombre": "Producto",
        "precio_neto": 1000,
        "forma_venta": FormaVenta.UNIDAD,
        "unidad_medida": UnidadMedida.UNIDAD,
        "controla_stock": True,
        "stock": Decimal("5"),
    }
    datos.update(extra)
    return Producto(**datos)


# ── Unicidad por tienda ─────────────────────────────────────────────────────


def test_el_codigo_no_se_repite_en_la_misma_tienda(tienda_a, crear_producto):
    crear_producto(tienda_a, codigo="REPETIDO")

    with pytest.raises(IntegrityError):
        producto(tienda_a, codigo="REPETIDO").save()


def test_dos_tiendas_pueden_usar_el_mismo_codigo(tienda_a, tienda_b, crear_producto):
    """El código es único por tienda, no en toda la plataforma."""
    crear_producto(tienda_a, codigo="PROD-01")
    crear_producto(tienda_b, codigo="PROD-01")

    assert Producto.objects.filter(codigo="PROD-01").count() == 2


def test_la_categoria_no_se_repite_en_la_misma_tienda(tienda_a):
    Categoria.objects.create(tienda=tienda_a, nombre="anillos")

    with pytest.raises(IntegrityError):
        Categoria.objects.create(tienda=tienda_a, nombre="anillos")


def test_una_categoria_no_se_repite_dentro_del_mismo_producto(tienda_a, crear_lote):
    lote = crear_lote(tienda_a)
    categoria = lote.composicion.first().categoria

    with pytest.raises(IntegrityError):
        ComposicionLote.objects.create(
            tienda=tienda_a, producto=lote, categoria=categoria, cantidad=2
        )


# ── Inventario ──────────────────────────────────────────────────────────────


def test_un_producto_que_controla_stock_tiene_que_decir_cuanto_hay(tienda_a):
    with pytest.raises(IntegrityError):
        producto(tienda_a, controla_stock=True, stock=None).save()


def test_un_producto_que_no_controla_stock_no_lleva_cantidad(tienda_a):
    with pytest.raises(IntegrityError):
        producto(tienda_a, controla_stock=False, stock=Decimal("5")).save()


def test_el_stock_no_puede_ser_negativo(tienda_a):
    with pytest.raises(IntegrityError):
        producto(tienda_a, stock=Decimal("-1")).save()


def test_el_stock_en_cero_esta_agotado(tienda_a, crear_producto):
    agotado = crear_producto(tienda_a, stock=Decimal("0"))

    assert agotado.agotado is True


def test_el_que_no_controla_stock_nunca_esta_agotado(tienda_a, granel_a):
    """La tienda no sabe cuánto le queda, así que no puede decir que se acabó."""
    assert granel_a.controla_stock is False
    assert granel_a.agotado is False


def test_el_stock_admite_decimales(tienda_a, crear_producto):
    """Un producto por peso se cuenta en gramos, y los gramos tienen decimales."""
    pesado = crear_producto(
        tienda_a,
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.GRAMO,
        stock=Decimal("125.500"),
    )
    pesado.refresh_from_db()

    assert pesado.stock == Decimal("125.500")


# ── La forma de venta manda sobre los demás campos ──────────────────────────


def test_un_producto_por_peso_no_se_mide_en_unidades(tienda_a):
    with pytest.raises(IntegrityError):
        producto(
            tienda_a,
            forma_venta=FormaVenta.PESO,
            unidad_medida=UnidadMedida.UNIDAD,
        ).save()


def test_un_producto_por_unidad_no_se_mide_en_gramos(tienda_a):
    with pytest.raises(IntegrityError):
        producto(
            tienda_a,
            forma_venta=FormaVenta.UNIDAD,
            unidad_medida=UnidadMedida.GRAMO,
        ).save()


def test_un_producto_por_peso_acepta_kilos(tienda_a):
    producto(
        tienda_a,
        forma_venta=FormaVenta.PESO,
        unidad_medida=UnidadMedida.KILO,
    ).save()

    assert Producto.objects.filter(unidad_medida=UnidadMedida.KILO).exists()


def test_solo_un_producto_por_lote_declara_piezas(tienda_a):
    with pytest.raises(IntegrityError):
        producto(tienda_a, forma_venta=FormaVenta.UNIDAD, cantidad_piezas=10).save()


def test_la_validacion_de_la_unidad_tambien_esta_en_clean(tienda_a, codigos_de_error):
    """La base es el último freno, pero el formulario tiene que explicarlo."""
    with pytest.raises(ValidationError) as error:
        producto(
            tienda_a,
            forma_venta=FormaVenta.PESO,
            unidad_medida=UnidadMedida.UNIDAD,
        ).full_clean()

    assert "unidad_no_corresponde" in codigos_de_error(error)


def test_clean_avisa_cuando_falta_el_stock(tienda_a, codigos_de_error):
    with pytest.raises(ValidationError) as error:
        producto(tienda_a, controla_stock=True, stock=None).full_clean()

    assert "stock_requerido" in codigos_de_error(error)


def test_el_precio_tiene_que_ser_positivo(tienda_a):
    with pytest.raises(IntegrityError):
        producto(tienda_a, precio_neto=0).save()


def test_la_cantidad_minima_tiene_que_ser_positiva(tienda_a):
    with pytest.raises(IntegrityError):
        producto(tienda_a, cantidad_minima=Decimal("0")).save()


# ── Composición del lote ────────────────────────────────────────────────────


def test_la_composicion_debe_sumar_la_cantidad_de_piezas(
    tienda_a, crear_lote, codigos_de_error
):
    lote = crear_lote(tienda_a, piezas=10)
    lote.cantidad_piezas = 12

    with pytest.raises(ValidationError) as error:
        lote.full_clean()

    assert "composicion_no_cuadra" in codigos_de_error(error)


def test_una_composicion_que_cuadra_pasa(tienda_a, crear_lote):
    crear_lote(tienda_a, piezas=10).full_clean()


def test_un_producto_recien_creado_sin_composicion_se_puede_guardar(tienda_a):
    """Exigir composición al crear impediría crear el lote en primer lugar."""
    lote = producto(
        tienda_a,
        forma_venta=FormaVenta.LOTE,
        cantidad_piezas=10,
        stock=Decimal("1"),
    )
    lote.save()
    lote.full_clean()


def test_la_composicion_no_acepta_una_categoria_de_otra_tienda(
    tienda_a, tienda_b, crear_lote, codigos_de_error
):
    """
    Una categoría ajena dentro de un lote sería una fuga por la puerta de
    atrás: su nombre quedaría visible en la vitrina de la otra tienda.
    """
    lote = crear_lote(tienda_a)
    ajena = Categoria.objects.create(tienda=tienda_b, nombre="de la otra")

    composicion = ComposicionLote(
        tienda=tienda_a, producto=lote, categoria=ajena, cantidad=1
    )

    with pytest.raises(ValidationError) as error:
        composicion.full_clean()

    assert "categoria_de_otra_tienda" in codigos_de_error(error)


def test_solo_un_producto_por_lote_tiene_composicion(
    tienda_a, crear_producto, codigos_de_error
):
    suelto = crear_producto(tienda_a)
    categoria = Categoria.objects.create(tienda=tienda_a, nombre="cocina")

    composicion = ComposicionLote(
        tienda=tienda_a, producto=suelto, categoria=categoria, cantidad=1
    )

    with pytest.raises(ValidationError) as error:
        composicion.full_clean()

    assert "composicion_solo_en_lote" in codigos_de_error(error)


# ── Qué llega a la vitrina ──────────────────────────────────────────────────


def test_la_vitrina_no_muestra_un_producto_desactivado(tienda_a, crear_producto):
    crear_producto(tienda_a, activo=False)

    assert not Producto.objects.publicadas_de(tienda_a).exists()


def test_la_vitrina_no_muestra_un_producto_agotado(tienda_a, crear_producto):
    crear_producto(tienda_a, stock=Decimal("0"))

    assert not Producto.objects.publicadas_de(tienda_a).exists()


def test_la_vitrina_muestra_un_producto_activo_con_stock(tienda_a, producto_a):
    assert producto_a in Producto.objects.publicadas_de(tienda_a)


def test_la_vitrina_muestra_lo_que_no_controla_stock(tienda_a, granel_a):
    """Sin inventario no hay nada que agotar: basta con que esté activo."""
    assert granel_a in Producto.objects.publicadas_de(tienda_a)


def test_la_vitrina_no_muestra_lo_que_no_controla_stock_si_esta_inactivo(
    tienda_a, crear_granel
):
    crear_granel(tienda_a, activo=False)

    assert not Producto.objects.publicadas_de(tienda_a).exists()
