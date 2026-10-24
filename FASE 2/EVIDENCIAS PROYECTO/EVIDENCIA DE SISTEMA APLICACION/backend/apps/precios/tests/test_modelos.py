"""
Restricciones de los tramos de precio.

Las sostiene la base, no el formulario: un tramo mal cargado no da error, da un
precio equivocado, y eso se descubre cuando ya se cobró.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.precios.models import TramoPrecio, UnidadUmbral

pytestmark = pytest.mark.django_db


def tramo(tienda, producto, **extra):
    datos = {
        "tienda": tienda,
        "producto": producto,
        "unidad_umbral": UnidadUmbral.CANTIDAD,
        "umbral": Decimal("12"),
        "valor": 4490,
    }
    datos.update(extra)
    return TramoPrecio(**datos)


# ── Unicidad ────────────────────────────────────────────────────────────────


def test_dos_tramos_del_mismo_producto_no_repiten_umbral(tienda_a, producto_a):
    """Dos tramos iguales se pisan: el motor no sabría cuál aplicar."""
    tramo(tienda_a, producto_a).save()

    with pytest.raises(IntegrityError):
        tramo(tienda_a, producto_a).save()


def test_el_mismo_umbral_en_otra_unidad_si_se_puede(tienda_a, producto_a):
    """500 unidades y 500 gramos son cosas distintas."""
    tramo(tienda_a, producto_a, unidad_umbral=UnidadUmbral.CANTIDAD).save()
    tramo(tienda_a, producto_a, unidad_umbral=UnidadUmbral.MONTO).save()

    assert TramoPrecio.objects.filter(producto=producto_a).count() == 2


def test_dos_productos_pueden_tener_el_mismo_umbral(
    tienda_a, producto_a, crear_producto
):
    otro = crear_producto(tienda_a, codigo="OTRO")

    tramo(tienda_a, producto_a).save()
    tramo(tienda_a, otro).save()

    assert TramoPrecio.objects.count() == 2


def test_dos_tiendas_pueden_tener_el_mismo_umbral(
    tienda_a, tienda_b, producto_a, producto_b
):
    tramo(tienda_a, producto_a).save()
    tramo(tienda_b, producto_b).save()

    assert TramoPrecio.objects.count() == 2


# ── Valores ─────────────────────────────────────────────────────────────────


def test_el_umbral_no_puede_ser_negativo(tienda_a, producto_a):
    with pytest.raises(IntegrityError):
        tramo(tienda_a, producto_a, umbral=Decimal("-1")).save()


def test_el_precio_tiene_que_ser_positivo(tienda_a, producto_a):
    with pytest.raises(IntegrityError):
        tramo(tienda_a, producto_a, valor=0).save()


def test_el_umbral_admite_decimales(tienda_a, producto_a):
    """Un umbral en peso puede ser medio gramo."""
    tramo(tienda_a, producto_a, umbral=Decimal("0.50")).save()

    assert TramoPrecio.objects.get().umbral == Decimal("0.50")


def test_un_tramo_necesita_un_producto(tienda_a):
    """No existen tramos de toda la tienda: un precio por volumen es de algo."""
    with pytest.raises(IntegrityError):
        TramoPrecio.objects.create(
            tienda=tienda_a,
            producto=None,
            unidad_umbral=UnidadUmbral.CANTIDAD,
            umbral=Decimal("12"),
            valor=4490,
        )


@pytest.mark.aislamiento
def test_un_tramo_no_cuelga_de_un_producto_de_otra_tienda(
    tienda_a, producto_b, codigos_de_error
):
    with pytest.raises(ValidationError) as error:
        tramo(tienda_a, producto_b).full_clean()

    assert "producto_de_otra_tienda" in codigos_de_error(error)
