"""Restricciones y validaciones del catálogo.

Lo que se prueba acá es que la base de datos sostiene las reglas por su cuenta.
Una validación que solo vive en un formulario se salta desde el admin, desde
una carga masiva o desde una vista nueva mal escrita.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.catalogo.models import Categoria, ComposicionLote, LineaGranel, Lote, TipoCupo

pytestmark = pytest.mark.django_db


# ── Unicidad por tienda ─────────────────────────────────────────────────────


def test_el_codigo_de_un_lote_no_se_repite_en_la_misma_tienda(tienda_a, crear_lote):
    crear_lote(tienda_a, codigo="REPETIDO")

    with pytest.raises(IntegrityError):
        Lote.objects.create(
            tienda=tienda_a,
            codigo="REPETIDO",
            nombre="Otro",
            cantidad_piezas=1,
            precio_neto=1000,
        )


def test_dos_tiendas_pueden_usar_el_mismo_codigo(tienda_a, tienda_b, crear_lote):
    """El código es único por tienda, no en toda la plataforma."""
    crear_lote(tienda_a, codigo="DEMO-01")
    crear_lote(tienda_b, codigo="DEMO-01")

    assert Lote.objects.filter(codigo="DEMO-01").count() == 2


def test_la_categoria_no_se_repite_en_la_misma_tienda(tienda_a):
    Categoria.objects.create(tienda=tienda_a, nombre="anillos")

    with pytest.raises(IntegrityError):
        Categoria.objects.create(tienda=tienda_a, nombre="anillos")


def test_el_codigo_de_granel_no_se_repite_en_la_misma_tienda(tienda_a, crear_granel):
    crear_granel(tienda_a, codigo="granel-hombre")

    with pytest.raises(IntegrityError):
        LineaGranel.objects.create(
            tienda=tienda_a, codigo="granel-hombre", nombre="Otra"
        )


def test_una_categoria_no_se_repite_dentro_del_mismo_lote(tienda_a, crear_lote):
    lote = crear_lote(tienda_a)
    categoria = lote.composicion.first().categoria

    with pytest.raises(IntegrityError):
        ComposicionLote.objects.create(
            tienda=tienda_a, lote=lote, categoria=categoria, cantidad=1
        )


# ── Cupos ───────────────────────────────────────────────────────────────────


def test_no_puede_haber_mas_cupos_libres_que_totales(tienda_a):
    with pytest.raises(IntegrityError):
        Lote.objects.create(
            tienda=tienda_a,
            codigo="MAL",
            nombre="Mal",
            cantidad_piezas=1,
            precio_neto=1000,
            cupos_totales=2,
            cupos_disponibles=5,
        )


def test_un_lote_de_cupo_unico_tiene_un_solo_cupo(tienda_a):
    with pytest.raises(IntegrityError):
        Lote.objects.create(
            tienda=tienda_a,
            codigo="UNICO-MAL",
            nombre="Mal",
            cantidad_piezas=1,
            precio_neto=1000,
            tipo_cupo=TipoCupo.UNICO,
            cupos_totales=4,
            cupos_disponibles=4,
        )


def test_el_cupo_unico_con_un_cupo_se_acepta(tienda_a):
    lote = Lote.objects.create(
        tienda=tienda_a,
        codigo="UNICO-OK",
        nombre="Pieza única",
        cantidad_piezas=1,
        precio_neto=1000,
        tipo_cupo=TipoCupo.UNICO,
        cupos_totales=1,
        cupos_disponibles=1,
    )

    assert lote.pk


def test_un_lote_sin_cupos_libres_esta_agotado(tienda_a, crear_lote):
    lote = crear_lote(tienda_a, cupos_totales=2, cupos_disponibles=0)

    assert lote.agotado


# ── Composición ─────────────────────────────────────────────────────────────


def test_la_composicion_debe_sumar_la_cantidad_de_piezas(
    tienda_a, crear_lote, codigos_de_error
):
    lote = crear_lote(tienda_a, piezas=10)
    lote.cantidad_piezas = 12

    with pytest.raises(ValidationError) as fallo:
        lote.full_clean()

    assert "composicion_no_cuadra" in codigos_de_error(fallo)


def test_una_composicion_que_cuadra_pasa(tienda_a, crear_lote):
    lote = crear_lote(tienda_a, piezas=10)

    lote.full_clean()


def test_un_lote_recien_creado_sin_composicion_se_puede_guardar(tienda_a):
    """Exigir la composición al crear impediría crear el lote."""
    lote = Lote(
        tienda=tienda_a,
        codigo="NUEVO",
        nombre="Nuevo",
        cantidad_piezas=5,
        precio_neto=1000,
    )

    lote.full_clean()


@pytest.mark.aislamiento
def test_la_composicion_no_acepta_una_categoria_de_otra_tienda(
    tienda_a, tienda_b, crear_lote, crear_categoria, codigos_de_error
):
    """
    Una categoría ajena dentro de un lote sería una fuga por la puerta de
    atrás: su nombre quedaría visible en la vitrina de la otra tienda.
    """
    lote = crear_lote(tienda_a)
    ajena = crear_categoria(tienda_b, nombre="categoria de B")

    composicion = ComposicionLote(
        tienda=tienda_a, lote=lote, categoria=ajena, cantidad=1
    )

    with pytest.raises(ValidationError) as fallo:
        composicion.full_clean()

    assert "categoria_de_otra_tienda" in codigos_de_error(fallo)


# ── Lo que ve la vitrina ────────────────────────────────────────────────────


def test_la_vitrina_no_muestra_un_lote_desactivado(tienda_a, crear_lote):
    crear_lote(tienda_a, codigo="OCULTO", activo=False)

    assert not Lote.objects.publicadas_de(tienda_a).filter(codigo="OCULTO").exists()


def test_la_vitrina_no_muestra_un_lote_agotado(tienda_a, crear_lote):
    crear_lote(tienda_a, codigo="AGOTADO", cupos_totales=2, cupos_disponibles=0)

    assert not Lote.objects.publicadas_de(tienda_a).filter(codigo="AGOTADO").exists()


def test_la_vitrina_muestra_un_lote_activo_con_cupos(tienda_a, lote_a):
    assert Lote.objects.publicadas_de(tienda_a).filter(pk=lote_a.pk).exists()


def test_la_vitrina_no_muestra_una_linea_de_granel_no_disponible(
    tienda_a, crear_granel
):
    crear_granel(tienda_a, codigo="apagada", disponible=False)

    assert (
        not LineaGranel.objects.publicadas_de(tienda_a)
        .filter(codigo="apagada")
        .exists()
    )
