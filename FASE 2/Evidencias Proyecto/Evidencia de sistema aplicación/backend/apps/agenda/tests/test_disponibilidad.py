"""
Cálculo de horas disponibles.

Cubre lo que pide el documento del módulo: horario partido, días bloqueados,
anticipación mínima, ventana máxima, capacidad llena y el cambio de horario de
Chile.
"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from apps.agenda.disponibilidad import asiento_libre, horas_disponibles, momento_local
from apps.agenda.models import BloqueHorario, DiaBloqueado, DiaSemana

pytestmark = pytest.mark.django_db

SANTIAGO = ZoneInfo("America/Santiago")

# Un lunes cualquiera, lejos de los cambios de horario de Chile.
LUNES = date(2026, 10, 5)
# El viernes anterior a las 09:00 de Chile: sirve como "ahora" en las pruebas.
AHORA = datetime(2026, 10, 2, 9, 0, tzinfo=SANTIAGO).astimezone(UTC)


def bloque(tienda, inicio=time(10, 0), fin=time(13, 0), **extra):
    datos = {
        "tienda": tienda,
        "dia_semana": DiaSemana.LUNES,
        "hora_inicio": inicio,
        "hora_fin": fin,
    }
    datos.update(extra)
    return BloqueHorario.objects.create(**datos)


def horas_del_lunes(configuracion, **extra):
    """Horas disponibles acotadas al lunes de referencia."""
    return horas_disponibles(
        configuracion, ahora=AHORA, desde=LUNES, hasta=LUNES, **extra
    )


def en_chile(momento):
    return momento.astimezone(SANTIAGO)


# ── Generación básica ───────────────────────────────────────────────────────


def test_un_bloque_de_tres_horas_con_visitas_de_treinta_minutos_da_seis_horas(
    tienda_a, configuracion_a
):
    bloque(tienda_a)

    horas = horas_del_lunes(configuracion_a)

    assert len(horas) == 6
    assert en_chile(horas[0].inicio).time() == time(10, 0)
    assert en_chile(horas[-1].inicio).time() == time(12, 30)


def test_la_ultima_hora_cabe_entera_dentro_del_bloque(tienda_a, configuracion_a):
    # 10:00 a 12:40 con visitas de 30 minutos: la de 12:30 no cabe.
    bloque(tienda_a, fin=time(12, 40))

    horas = horas_del_lunes(configuracion_a)

    assert en_chile(horas[-1].inicio).time() == time(12, 0)


def test_sin_bloques_no_hay_horas(tienda_a, configuracion_a):
    assert horas_del_lunes(configuracion_a) == []


# ── Horario partido ─────────────────────────────────────────────────────────


def test_el_horario_partido_no_ofrece_horas_en_la_pausa(tienda_a, configuracion_a):
    bloque(tienda_a, inicio=time(10, 0), fin=time(13, 0))
    bloque(tienda_a, inicio=time(15, 0), fin=time(18, 0))

    horas = [en_chile(hora.inicio).time() for hora in horas_del_lunes(configuracion_a)]

    assert time(12, 30) in horas
    assert time(15, 0) in horas
    assert not any(time(13, 0) <= hora < time(15, 0) for hora in horas)


# ── Personalización por bloque ──────────────────────────────────────────────


def test_cada_bloque_usa_su_propia_duracion(tienda_a, configuracion_a):
    bloque(tienda_a, inicio=time(10, 0), fin=time(12, 0))  # hereda 30 minutos
    bloque(tienda_a, inicio=time(15, 0), fin=time(18, 0), duracion_minutos=60)

    horas = [en_chile(hora.inicio).time() for hora in horas_del_lunes(configuracion_a)]

    assert horas == [
        time(10, 0),
        time(10, 30),
        time(11, 0),
        time(11, 30),
        time(15, 0),
        time(16, 0),
        time(17, 0),
    ]


def test_cada_bloque_informa_su_forma_de_confirmacion(tienda_a, configuracion_a):
    bloque(tienda_a, inicio=time(10, 0), fin=time(11, 0))
    bloque(tienda_a, inicio=time(15, 0), fin=time(16, 0), confirmacion_automatica=True)

    horas = horas_del_lunes(configuracion_a)
    manana = [h for h in horas if en_chile(h.inicio).hour == 10]
    tarde = [h for h in horas if en_chile(h.inicio).hour == 15]

    assert all(h.confirmacion_automatica is False for h in manana)
    assert all(h.confirmacion_automatica is True for h in tarde)


def test_un_bloque_puntual_solo_ofrece_horas_ese_dia(tienda_a, configuracion_a):
    sabado = date(2026, 10, 10)
    bloque(tienda_a, dia_semana=None, fecha=sabado, inicio=time(10, 0), fin=time(11, 0))

    del_sabado = horas_disponibles(
        configuracion_a, ahora=AHORA, desde=sabado, hasta=sabado
    )
    del_sabado_siguiente = horas_disponibles(
        configuracion_a, ahora=AHORA, desde=date(2026, 10, 17), hasta=date(2026, 10, 17)
    )

    assert len(del_sabado) == 2
    assert del_sabado_siguiente == []


# ── Días bloqueados, anticipación y ventana ─────────────────────────────────


def test_un_dia_bloqueado_no_ofrece_horas(tienda_a, configuracion_a):
    bloque(tienda_a)
    DiaBloqueado.objects.create(tienda=tienda_a, fecha=LUNES, motivo="Feriado")

    assert horas_del_lunes(configuracion_a) == []


def test_no_se_ofrecen_horas_antes_de_la_anticipacion_minima(tienda_a, configuracion_a):
    bloque(tienda_a)
    # El mismo lunes a las 09:00 de Chile: con 24 horas de anticipación, ninguna
    # hora de ese día alcanza.
    ahora = datetime(2026, 10, 5, 9, 0, tzinfo=SANTIAGO).astimezone(UTC)

    horas = horas_disponibles(configuracion_a, ahora=ahora, desde=LUNES, hasta=LUNES)

    assert horas == []


def test_no_se_ofrecen_horas_mas_alla_de_la_ventana_maxima(tienda_a, configuracion_a):
    bloque(tienda_a)
    configuracion_a.ventana_maxima_dias = 1
    configuracion_a.save()

    horas = horas_disponibles(configuracion_a, ahora=AHORA)

    assert horas == []


# ── Capacidad ───────────────────────────────────────────────────────────────


def test_una_hora_llena_no_se_ofrece(tienda_a, configuracion_a, crear_visita):
    bloque(tienda_a, inicio=time(10, 0), fin=time(10, 30))
    inicio = momento_local(LUNES, time(10, 0))
    crear_visita(tienda_a, inicio=inicio, fin=inicio + timedelta(minutes=30))

    assert horas_del_lunes(configuracion_a) == []


def test_una_hora_con_capacidad_de_sobra_informa_los_cupos_libres(
    tienda_a, configuracion_a, crear_visita
):
    bloque(tienda_a, inicio=time(10, 0), fin=time(10, 30), visitas_simultaneas=3)
    inicio = momento_local(LUNES, time(10, 0))
    crear_visita(tienda_a, inicio=inicio, fin=inicio + timedelta(minutes=30))

    horas = horas_del_lunes(configuracion_a)

    assert len(horas) == 1
    assert horas[0].cupos_libres == 2


def test_una_visita_cancelada_devuelve_el_cupo(tienda_a, configuracion_a, crear_visita):
    from apps.agenda.models import EstadoVisita

    bloque(tienda_a, inicio=time(10, 0), fin=time(10, 30))
    inicio = momento_local(LUNES, time(10, 0))
    visita = crear_visita(tienda_a, inicio=inicio, fin=inicio + timedelta(minutes=30))
    visita.cambiar_estado(EstadoVisita.CANCELADA)
    visita.save()

    assert len(horas_del_lunes(configuracion_a)) == 1


# ── Cambio de horario de Chile ──────────────────────────────────────────────


def test_una_hora_despues_del_cambio_de_horario_queda_a_la_misma_hora_local():
    # Chile adelanta el reloj el primer sábado de septiembre de 2026.
    antes = momento_local(date(2026, 8, 31), time(10, 0))
    despues = momento_local(date(2026, 9, 7), time(10, 0))

    assert en_chile(antes).time() == time(10, 0)
    assert en_chile(despues).time() == time(10, 0)
    # El desfase con UTC cambia, que es justo lo que corre las visitas cuando se
    # guardan en hora local.
    assert antes.hour != despues.hour


# ── Asientos ────────────────────────────────────────────────────────────────


def test_el_primer_asiento_libre_es_el_cero(tienda_a):
    inicio = momento_local(LUNES, time(10, 0))

    assert asiento_libre(tienda_a.id, inicio, capacidad=2) == 0


def test_el_asiento_libre_salta_los_tomados(tienda_a, crear_visita):
    inicio = momento_local(LUNES, time(10, 0))
    crear_visita(
        tienda_a, inicio=inicio, fin=inicio + timedelta(minutes=30), posicion=0
    )

    assert asiento_libre(tienda_a.id, inicio, capacidad=2) == 1


def test_sin_asientos_libres_devuelve_nada(tienda_a, crear_visita):
    inicio = momento_local(LUNES, time(10, 0))
    crear_visita(
        tienda_a, inicio=inicio, fin=inicio + timedelta(minutes=30), posicion=0
    )

    assert asiento_libre(tienda_a.id, inicio, capacidad=1) is None


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_las_visitas_de_otra_tienda_no_ocupan_cupo(
    tienda_a, tienda_b, configuracion_a, crear_visita
):
    bloque(tienda_a, inicio=time(10, 0), fin=time(10, 30))
    inicio = momento_local(LUNES, time(10, 0))
    crear_visita(tienda_b, inicio=inicio, fin=inicio + timedelta(minutes=30))

    horas = horas_del_lunes(configuracion_a)

    assert len(horas) == 1
    assert horas[0].cupos_libres == 1


@pytest.mark.aislamiento
def test_los_bloques_de_otra_tienda_no_generan_horas(
    tienda_a, tienda_b, configuracion_a
):
    bloque(tienda_b)

    assert horas_del_lunes(configuracion_a) == []
