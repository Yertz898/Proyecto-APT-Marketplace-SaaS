"""
Bloques de atención personalizables.

Cada bloque puede definir su propia duración, capacidad, nombre y forma de
confirmación. Lo que no define, lo hereda de la configuración de la tienda.
"""

from datetime import date, time

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.agenda.models import BloqueHorario, DiaSemana

pytestmark = pytest.mark.django_db


def crear_bloque(tienda, **extra):
    datos = {
        "tienda": tienda,
        "dia_semana": DiaSemana.LUNES,
        "hora_inicio": time(10, 0),
        "hora_fin": time(13, 0),
    }
    datos.update(extra)
    return BloqueHorario.objects.create(**datos)


# ── Herencia de la configuración de la tienda ───────────────────────────────


def test_un_bloque_sin_duracion_usa_la_de_la_tienda(tienda_a, configuracion_a):
    bloque = crear_bloque(tienda_a)

    assert bloque.duracion(configuracion_a) == configuracion_a.duracion_minutos


def test_un_bloque_con_duracion_propia_la_usa(tienda_a, configuracion_a):
    bloque = crear_bloque(tienda_a, duracion_minutos=60)

    assert configuracion_a.duracion_minutos != 60
    assert bloque.duracion(configuracion_a) == 60


def test_un_bloque_sin_capacidad_usa_la_de_la_tienda(tienda_a, configuracion_a):
    bloque = crear_bloque(tienda_a)

    assert bloque.capacidad(configuracion_a) == configuracion_a.visitas_por_bloque


def test_un_bloque_con_capacidad_propia_la_usa(tienda_a, configuracion_a):
    bloque = crear_bloque(tienda_a, visitas_simultaneas=3)

    assert bloque.capacidad(configuracion_a) == 3


def test_un_bloque_hereda_la_forma_de_confirmacion(tienda_a, configuracion_a):
    bloque = crear_bloque(tienda_a)

    assert (
        bloque.confirma_solo(configuracion_a) is configuracion_a.confirmacion_automatica
    )


def test_un_bloque_puede_confirmar_solo_aunque_la_tienda_no(tienda_a, configuracion_a):
    assert configuracion_a.confirmacion_automatica is False

    bloque = crear_bloque(tienda_a, confirmacion_automatica=True)

    assert bloque.confirma_solo(configuracion_a) is True


def test_un_bloque_puede_pedir_aprobacion_aunque_la_tienda_confirme_sola(
    tienda_a, configuracion_a
):
    configuracion_a.confirmacion_automatica = True
    configuracion_a.save()

    bloque = crear_bloque(tienda_a, confirmacion_automatica=False)

    assert bloque.confirma_solo(configuracion_a) is False


# ── Bloques semanales y de fecha puntual ────────────────────────────────────


def test_un_bloque_semanal_aplica_en_su_dia(tienda_a):
    bloque = crear_bloque(tienda_a, dia_semana=DiaSemana.LUNES)

    assert bloque.aplica_en(date(2026, 10, 5)) is True  # lunes
    assert bloque.aplica_en(date(2026, 10, 6)) is False  # martes


def test_un_bloque_puntual_aplica_solo_en_su_fecha(tienda_a):
    bloque = crear_bloque(tienda_a, dia_semana=None, fecha=date(2026, 10, 10))

    assert bloque.es_puntual
    assert bloque.aplica_en(date(2026, 10, 10)) is True
    assert bloque.aplica_en(date(2026, 10, 17)) is False  # mismo día de la semana


def test_un_bloque_no_puede_ser_semanal_y_puntual_a_la_vez(tienda_a):
    with pytest.raises(IntegrityError):
        crear_bloque(tienda_a, dia_semana=DiaSemana.LUNES, fecha=date(2026, 10, 10))


def test_un_bloque_necesita_dia_o_fecha(tienda_a):
    with pytest.raises(IntegrityError):
        crear_bloque(tienda_a, dia_semana=None)


# ── Validaciones ────────────────────────────────────────────────────────────


def test_dos_bloques_del_mismo_dia_no_se_pueden_solapar(tienda_a):
    crear_bloque(tienda_a, hora_inicio=time(10, 0), hora_fin=time(13, 0))

    solapado = BloqueHorario(
        tienda=tienda_a,
        dia_semana=DiaSemana.LUNES,
        hora_inicio=time(12, 0),
        hora_fin=time(15, 0),
    )

    with pytest.raises(ValidationError):
        solapado.full_clean()


def test_dos_bloques_del_mismo_dia_que_no_se_tocan_conviven(tienda_a):
    crear_bloque(tienda_a, hora_inicio=time(10, 0), hora_fin=time(13, 0))

    tarde = BloqueHorario(
        tienda=tienda_a,
        dia_semana=DiaSemana.LUNES,
        hora_inicio=time(15, 0),
        hora_fin=time(18, 0),
    )
    tarde.full_clean()
    tarde.save()

    assert BloqueHorario.objects.de_tienda(tienda_a).count() == 2


@pytest.mark.aislamiento
def test_el_bloque_de_otra_tienda_no_estorba(tienda_a, tienda_b):
    crear_bloque(tienda_b, hora_inicio=time(10, 0), hora_fin=time(13, 0))

    mismo_horario = BloqueHorario(
        tienda=tienda_a,
        dia_semana=DiaSemana.LUNES,
        hora_inicio=time(10, 0),
        hora_fin=time(13, 0),
    )
    mismo_horario.full_clean()
    mismo_horario.save()

    assert BloqueHorario.objects.de_tienda(tienda_a).count() == 1
    assert BloqueHorario.objects.de_tienda(tienda_b).count() == 1
