"""Estados de una visita, capacidad del bloque y token del feed."""

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.agenda.models import EstadoVisita, Visita

pytestmark = pytest.mark.django_db


# ── Transiciones de estado ──────────────────────────────────────────────────


def test_una_solicitud_se_puede_confirmar(visita_a):
    visita_a.cambiar_estado(EstadoVisita.CONFIRMADA)

    assert visita_a.estado == EstadoVisita.CONFIRMADA


def test_una_visita_cancelada_no_se_puede_confirmar(visita_a):
    visita_a.cambiar_estado(EstadoVisita.CANCELADA)

    with pytest.raises(ValidationError) as error:
        visita_a.cambiar_estado(EstadoVisita.CONFIRMADA)

    assert "estado" in error.value.message_dict


def test_una_solicitud_no_puede_saltar_a_asistida(visita_a):
    with pytest.raises(ValidationError):
        visita_a.cambiar_estado(EstadoVisita.ASISTIDA)


def test_rechazar_guarda_el_motivo(visita_a):
    visita_a.cambiar_estado(
        EstadoVisita.RECHAZADA, motivo_rechazo="Ese día no atendemos."
    )

    assert visita_a.estado == EstadoVisita.RECHAZADA
    assert visita_a.motivo_rechazo == "Ese día no atendemos."


# ── Secuencia del evento de calendario ──────────────────────────────────────


def test_confirmar_aumenta_la_secuencia(visita_a):
    secuencia_inicial = visita_a.secuencia

    visita_a.cambiar_estado(EstadoVisita.CONFIRMADA)

    assert visita_a.secuencia == secuencia_inicial + 1


def test_marcar_asistida_no_toca_el_calendario(visita_a):
    visita_a.cambiar_estado(EstadoVisita.CONFIRMADA)
    secuencia = visita_a.secuencia

    visita_a.cambiar_estado(EstadoVisita.ASISTIDA)

    assert visita_a.secuencia == secuencia


def test_reprogramar_conserva_el_identificador_y_aumenta_la_secuencia(visita_a):
    uid_original = visita_a.uid
    secuencia = visita_a.secuencia
    nuevo_inicio = visita_a.inicio.replace(hour=16)

    visita_a.reprogramar(nuevo_inicio, nuevo_inicio + (visita_a.fin - visita_a.inicio))

    assert visita_a.uid == uid_original
    assert visita_a.secuencia == secuencia + 1
    assert visita_a.inicio == nuevo_inicio


def test_no_se_puede_reprogramar_una_visita_cancelada(visita_a):
    visita_a.cambiar_estado(EstadoVisita.CANCELADA)

    with pytest.raises(ValidationError):
        visita_a.reprogramar(visita_a.inicio, visita_a.fin)


# ── Capacidad del bloque ────────────────────────────────────────────────────


def test_dos_visitas_no_pueden_tomar_el_mismo_asiento(tienda_a, visita_a, crear_visita):
    with pytest.raises(IntegrityError):
        crear_visita(tienda_a, posicion=visita_a.posicion)


def test_el_segundo_asiento_del_mismo_bloque_si_se_puede_tomar(
    tienda_a, visita_a, crear_visita
):
    segunda = crear_visita(tienda_a, posicion=1)

    assert segunda.inicio == visita_a.inicio
    assert Visita.objects.de_tienda(tienda_a).count() == 2


def test_una_visita_cancelada_libera_su_asiento(tienda_a, visita_a, crear_visita):
    visita_a.cambiar_estado(EstadoVisita.CANCELADA)
    visita_a.save()

    reemplazo = crear_visita(tienda_a, posicion=visita_a.posicion)

    assert reemplazo.ocupa_cupo


# ── Feed de calendario ──────────────────────────────────────────────────────


def test_regenerar_el_token_invalida_el_anterior(configuracion_a):
    token_anterior = configuracion_a.token_feed

    token_nuevo = configuracion_a.regenerar_token_feed()

    assert token_nuevo != token_anterior
    assert len(token_nuevo) >= 32


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_el_dueno_no_ve_visitas_de_otra_tienda(visita_a, visita_b, dueno_a):
    visibles = Visita.objects.de_usuario(dueno_a)

    assert list(visibles) == [visita_a]
    assert visita_b not in visibles
