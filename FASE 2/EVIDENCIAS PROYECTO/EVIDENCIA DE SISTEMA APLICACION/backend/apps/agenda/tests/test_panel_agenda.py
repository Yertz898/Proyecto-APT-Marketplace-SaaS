"""La agenda desde el panel: horarios, días cerrados y visitas."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.agenda.models import BloqueHorario, EstadoVisita, Visita
from apps.tiendas.models import Plan

pytestmark = pytest.mark.django_db


def como(usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(usuario)}")
    return cliente


@pytest.fixture
def premium(tienda_a, tienda_b):
    for tienda in (tienda_a, tienda_b):
        tienda.plan = Plan.PREMIUM
        tienda.save()


def _visita(tienda, comprador, **extra):
    inicio = timezone.now() + timedelta(days=2)
    return Visita.objects.create(
        tienda=tienda,
        inicio=inicio,
        fin=inicio + timedelta(minutes=30),
        nombre_contacto="Paula",
        correo_contacto="paula@ejemplo.cl",
        telefono_contacto="+56911111111",
        comprador=comprador,
        **extra,
    )


def test_la_configuracion_se_crea_al_pedirla(premium, dueno_a):
    respuesta = como(dueno_a).get("/api/panel/agenda/configuracion")

    assert respuesta.status_code == 200
    assert respuesta.json()["duracionMinutos"] == 30


def test_el_plan_basico_no_tiene_agenda(dueno_a):
    assert como(dueno_a).get("/api/panel/agenda/configuracion").status_code == 403


def test_crea_un_bloque_y_rechaza_uno_que_se_cruza(premium, dueno_a, tienda_a):
    cliente = como(dueno_a)
    bloque = {"diaSemana": 0, "horaInicio": "10:00", "horaFin": "13:00"}

    assert (
        cliente.post("/api/panel/agenda/bloques", bloque, format="json").status_code
        == 201
    )
    cruzado = {"diaSemana": 0, "horaInicio": "12:00", "horaFin": "14:00"}
    assert (
        cliente.post("/api/panel/agenda/bloques", cruzado, format="json").status_code
        == 400
    )
    assert BloqueHorario.objects.filter(tienda=tienda_a).count() == 1


def test_no_ve_ni_borra_bloques_de_otra_tienda(premium, dueno_a, tienda_b):
    ajeno = BloqueHorario.objects.create(
        tienda=tienda_b,
        dia_semana=1,
        hora_inicio="09:00",
        hora_fin="10:00",
    )
    cliente = como(dueno_a)

    assert cliente.get("/api/panel/agenda/bloques").json() == []
    assert cliente.delete(f"/api/panel/agenda/bloques/{ajeno.pk}").status_code == 404


def test_confirma_una_visita_solicitada(premium, dueno_a, tienda_a, comprador):
    visita = _visita(tienda_a, comprador)

    respuesta = como(dueno_a).post(
        f"/api/panel/agenda/visitas/{visita.pk}/estado",
        {"estado": EstadoVisita.CONFIRMADA},
        format="json",
    )

    assert respuesta.status_code == 200
    visita.refresh_from_db()
    assert visita.estado == EstadoVisita.CONFIRMADA


def test_una_transicion_invalida_responde_400(premium, dueno_a, tienda_a, comprador):
    visita = _visita(tienda_a, comprador)

    respuesta = como(dueno_a).post(
        f"/api/panel/agenda/visitas/{visita.pk}/estado",
        {"estado": EstadoVisita.ASISTIDA},
        format="json",
    )

    assert respuesta.status_code == 400


def test_no_toca_visitas_de_otra_tienda(premium, dueno_a, tienda_b, comprador):
    ajena = _visita(tienda_b, comprador)
    cliente = como(dueno_a)

    assert cliente.get("/api/panel/agenda/visitas").json() == []
    assert (
        cliente.post(
            f"/api/panel/agenda/visitas/{ajena.pk}/estado",
            {"estado": EstadoVisita.CONFIRMADA},
            format="json",
        ).status_code
        == 404
    )


def test_cierra_un_dia_una_sola_vez(premium, dueno_a):
    cliente = como(dueno_a)
    manana = (timezone.localdate() + timedelta(days=1)).isoformat()

    assert (
        cliente.post(
            "/api/panel/agenda/dias-cerrados", {"fecha": manana}, format="json"
        ).status_code
        == 201
    )
    assert (
        cliente.post(
            "/api/panel/agenda/dias-cerrados", {"fecha": manana}, format="json"
        ).status_code
        == 400
    )
    assert len(cliente.get("/api/panel/agenda/dias-cerrados").json()) == 1


def test_confirmar_una_hora_ya_tomada_se_rechaza(premium, dueno_a, tienda_a, comprador):
    primera = _visita(tienda_a, comprador)
    segunda = Visita.objects.create(
        tienda=tienda_a,
        inicio=primera.inicio,
        fin=primera.fin,
        nombre_contacto="Otra",
        correo_contacto="otra@ejemplo.cl",
        telefono_contacto="+56922222222",
        comprador=comprador,
    )
    cliente = como(dueno_a)
    url = "/api/panel/agenda/visitas/{}/estado"

    confirmada = cliente.post(
        url.format(primera.pk), {"estado": EstadoVisita.CONFIRMADA}, format="json"
    )
    assert confirmada.status_code == 200

    visitas = {v["id"]: v for v in cliente.get("/api/panel/agenda/visitas").json()}
    assert visitas[segunda.pk]["horaTomada"] is True

    choque = cliente.post(
        url.format(segunda.pk), {"estado": EstadoVisita.CONFIRMADA}, format="json"
    )
    assert choque.status_code == 400
    segunda.refresh_from_db()
    assert segunda.estado == EstadoVisita.SOLICITADA
