"""
Reagendar: proponer otra hora, responderla, y los avisos que deja cada paso.

Lo que no puede fallar: que responda la otra parte y no la que propuso, que
rechazar cancele la visita, que mover una visita confirmada respete el cupo,
que nadie toque visitas de otra tienda, y que con los correos apagados no
salga ninguno (pero queden registrados).
"""

from datetime import time, timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.agenda import avisos
from apps.agenda.disponibilidad import momento_local
from apps.agenda.models import (
    BloqueHorario,
    CambioDeHora,
    ConfiguracionAgenda,
    EnvioCorreo,
    EstadoDelCambio,
    EstadoEnvio,
    EstadoVisita,
    TipoCorreo,
    Visita,
)
from apps.tiendas.models import Plan

pytestmark = pytest.mark.django_db


def como(usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    cliente = APIClient(SERVER_NAME="localhost")
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(usuario)}")
    return cliente


@pytest.fixture
def dia():
    return (timezone.localtime() + timedelta(days=3)).date()


@pytest.fixture
def agenda_a(tienda_a, tienda_b, dia):
    for tienda in (tienda_a, tienda_b):
        tienda.plan = Plan.PREMIUM
        tienda.save()
    ConfiguracionAgenda.objects.create(tienda=tienda_a)
    BloqueHorario.objects.create(
        tienda=tienda_a,
        dia_semana=dia.weekday(),
        hora_inicio=time(10, 0),
        hora_fin=time(12, 0),
    )
    return tienda_a


def a_las(dia, hora, minuto=0):
    return momento_local(dia, time(hora, minuto))


@pytest.fixture
def visita(agenda_a, comprador, dueno_a, dia):
    """Una visita confirmada a las 10:00 en la tienda A."""
    inicio = a_las(dia, 10)
    return Visita.objects.create(
        tienda=agenda_a,
        comprador=comprador,
        inicio=inicio,
        fin=inicio + timedelta(minutes=30),
        estado=EstadoVisita.CONFIRMADA,
        nombre_contacto="Camila Rojas",
        correo_contacto="camila@ejemplo.cl",
        telefono_contacto="+56912345678",
    )


def proponer_como_cliente(comprador, visita, inicio):
    return como(comprador).post(
        f"/api/t/{visita.tienda.slug}/agenda/mis-visitas/{visita.pk}/cambio",
        {"inicio": inicio.isoformat()},
        format="json",
    )


def responder_como_cliente(comprador, visita, acepta):
    return como(comprador).post(
        f"/api/t/{visita.tienda.slug}/agenda/mis-visitas/{visita.pk}/cambio/respuesta",
        {"acepta": acepta},
        format="json",
    )


def proponer_como_tienda(usuario, visita, inicio):
    return como(usuario).post(
        f"/api/panel/agenda/visitas/{visita.pk}/cambio",
        {"inicio": inicio.isoformat()},
        format="json",
    )


def responder_como_tienda(usuario, visita, acepta):
    return como(usuario).post(
        f"/api/panel/agenda/visitas/{visita.pk}/cambio/respuesta",
        {"acepta": acepta},
        format="json",
    )


# ── El cliente propone, la tienda responde ──────────────────────────────────


def test_el_cliente_propone_y_la_tienda_lo_ve_en_su_panel(
    comprador, dueno_a, visita, dia, mailoutbox
):
    respuesta = proponer_como_cliente(comprador, visita, a_las(dia, 11))

    assert respuesta.status_code == 201
    assert respuesta.json()["cambioPendiente"]["propuestoPor"] == "comprador"

    panel = como(dueno_a).get("/api/panel/agenda/visitas").json()
    (fila,) = panel
    assert fila["cambioPendiente"]["propuestoPor"] == "comprador"

    # El aviso queda registrado para el dueño, pero no sale ningún correo.
    (aviso,) = EnvioCorreo.objects.filter(tipo=TipoCorreo.CAMBIO_PROPUESTO)
    assert aviso.destinatario == dueno_a.email
    assert aviso.estado == EstadoEnvio.PENDIENTE
    assert "aceptar" in aviso.cuerpo
    assert mailoutbox == []


def test_la_tienda_acepta_y_la_visita_se_mueve(comprador, dueno_a, visita, dia):
    proponer_como_cliente(comprador, visita, a_las(dia, 11))

    respuesta = responder_como_tienda(dueno_a, visita, True)

    assert respuesta.status_code == 200
    visita.refresh_from_db()
    assert visita.inicio == a_las(dia, 11)
    assert visita.estado == EstadoVisita.CONFIRMADA
    assert visita.cambios.get().estado == EstadoDelCambio.ACEPTADO
    # Se les avisa a las dos partes.
    assert EnvioCorreo.objects.filter(tipo=TipoCorreo.REPROGRAMADA).count() == 2


def test_la_tienda_rechaza_y_la_visita_se_cancela(comprador, dueno_a, visita, dia):
    proponer_como_cliente(comprador, visita, a_las(dia, 11))

    responder_como_tienda(dueno_a, visita, False)

    visita.refresh_from_db()
    assert visita.estado == EstadoVisita.CANCELADA
    assert visita.inicio == a_las(dia, 10)
    aviso = EnvioCorreo.objects.get(tipo=TipoCorreo.CANCELADA)
    assert aviso.destinatario == "camila@ejemplo.cl"


def test_quien_propone_no_puede_responderse_a_si_mismo(comprador, visita, dia):
    proponer_como_cliente(comprador, visita, a_las(dia, 11))

    respuesta = responder_como_cliente(comprador, visita, True)

    assert respuesta.status_code == 400
    visita.refresh_from_db()
    assert visita.inicio == a_las(dia, 10)


def test_no_se_acumulan_dos_propuestas(comprador, dueno_a, visita, dia):
    proponer_como_cliente(comprador, visita, a_las(dia, 11))

    respuesta = proponer_como_tienda(dueno_a, visita, a_las(dia, 11, 30))

    assert respuesta.status_code == 400
    assert CambioDeHora.objects.count() == 1


# ── La tienda propone, el cliente responde ──────────────────────────────────


def test_la_tienda_propone_y_el_cliente_acepta_desde_sus_citas(
    comprador, dueno_a, visita, dia
):
    assert proponer_como_tienda(dueno_a, visita, a_las(dia, 11, 30)).status_code == 201

    citas = (
        como(comprador).get(f"/api/t/{visita.tienda.slug}/agenda/mis-visitas").json()
    )
    assert citas[0]["cambioPendiente"]["propuestoPor"] == "tienda"

    respuesta = responder_como_cliente(comprador, visita, True)

    assert respuesta.status_code == 200
    visita.refresh_from_db()
    assert visita.inicio == a_las(dia, 11, 30)


# ── Reglas de la hora ───────────────────────────────────────────────────────


def test_no_se_propone_una_hora_que_la_agenda_no_ofrece(comprador, visita, dia):
    respuesta = proponer_como_cliente(comprador, visita, a_las(dia, 9))

    assert respuesta.status_code == 400
    assert not CambioDeHora.objects.exists()


def test_aceptar_respeta_el_cupo_de_la_hora_nueva(comprador, dueno_a, visita, dia):
    proponer_como_cliente(comprador, visita, a_las(dia, 11))
    # Mientras tanto la tienda confirmó a otra persona a esa hora (cupo de 1).
    Visita.objects.create(
        tienda=visita.tienda,
        comprador=comprador,
        inicio=a_las(dia, 11),
        fin=a_las(dia, 11, 30),
        estado=EstadoVisita.CONFIRMADA,
        nombre_contacto="Otra",
        correo_contacto="otra@ejemplo.cl",
        telefono_contacto="+56987654321",
    )

    respuesta = responder_como_tienda(dueno_a, visita, True)

    assert respuesta.status_code == 400
    visita.refresh_from_db()
    assert visita.inicio == a_las(dia, 10)
    assert visita.cambios.get().estado == EstadoDelCambio.PENDIENTE


# ── Cancelar ────────────────────────────────────────────────────────────────


def test_el_cliente_cancela_y_se_anula_el_cambio_pendiente(
    comprador, dueno_a, visita, dia
):
    proponer_como_tienda(dueno_a, visita, a_las(dia, 11))

    respuesta = como(comprador).post(
        f"/api/t/{visita.tienda.slug}/agenda/mis-visitas/{visita.pk}/cancelar"
    )

    assert respuesta.status_code == 200
    visita.refresh_from_db()
    assert visita.estado == EstadoVisita.CANCELADA
    assert visita.cambios.get().estado == EstadoDelCambio.ANULADO
    aviso = EnvioCorreo.objects.get(tipo=TipoCorreo.CANCELADA)
    assert aviso.destinatario == dueno_a.email


def test_cuando_la_tienda_cancela_se_le_avisa_al_cliente(dueno_a, visita):
    respuesta = como(dueno_a).post(
        f"/api/panel/agenda/visitas/{visita.pk}/estado",
        {"estado": EstadoVisita.CANCELADA},
        format="json",
    )

    assert respuesta.status_code == 200
    aviso = EnvioCorreo.objects.get(tipo=TipoCorreo.CANCELADA)
    assert aviso.destinatario == "camila@ejemplo.cl"


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_otra_tienda_no_toca_la_visita(dueno_b, visita, dia):
    assert proponer_como_tienda(dueno_b, visita, a_las(dia, 11)).status_code == 404
    assert responder_como_tienda(dueno_b, visita, True).status_code == 404


@pytest.mark.aislamiento
def test_la_visita_no_se_ve_desde_otra_tienda(comprador, visita, tienda_b):
    respuesta = como(comprador).post(
        f"/api/t/{tienda_b.slug}/agenda/mis-visitas/{visita.pk}/cancelar"
    )

    assert respuesta.status_code == 404
    visita.refresh_from_db()
    assert visita.estado == EstadoVisita.CONFIRMADA


# ── Correos: apagados por omisión, listos al encenderlos ────────────────────


def test_con_los_correos_encendidos_el_aviso_sale(
    comprador, visita, dia, settings, mailoutbox, django_capture_on_commit_callbacks
):
    settings.CORREOS_AGENDA_ACTIVOS = True
    settings.RESEND_API_KEY = ""

    with django_capture_on_commit_callbacks(execute=True):
        proponer_como_cliente(comprador, visita, a_las(dia, 11))

    assert len(mailoutbox) == 1
    assert "pide cambiar su visita" in mailoutbox[0].subject
    aviso = EnvioCorreo.objects.get(tipo=TipoCorreo.CAMBIO_PROPUESTO)
    assert aviso.estado == EstadoEnvio.ENVIADO


def test_el_enlace_del_correo_responde_una_sola_vez(comprador, visita, dia):
    proponer_como_cliente(comprador, visita, a_las(dia, 11))
    firma = avisos.firmar_cambio(CambioDeHora.objects.get())
    anonimo = APIClient(SERVER_NAME="localhost")

    detalle = anonimo.get("/api/agenda/cambios/enlace", {"firma": firma})
    assert detalle.status_code == 200
    assert detalle.json()["responde"] == "tienda"

    primera = anonimo.post(
        "/api/agenda/cambios/enlace", {"firma": firma, "acepta": True}, format="json"
    )
    assert primera.status_code == 200
    visita.refresh_from_db()
    assert visita.inicio == a_las(dia, 11)

    segunda = anonimo.post(
        "/api/agenda/cambios/enlace", {"firma": firma, "acepta": False}, format="json"
    )
    assert segunda.status_code == 400


def test_un_enlace_falso_no_sirve(visita):
    respuesta = APIClient(SERVER_NAME="localhost").post(
        "/api/agenda/cambios/enlace",
        {"firma": "inventada", "acepta": True},
        format="json",
    )

    assert respuesta.status_code == 400
