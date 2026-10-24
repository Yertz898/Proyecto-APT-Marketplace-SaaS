"""Reserva de una visita: POST /t/<slug>/agenda/visitas."""

from datetime import time, timedelta

import pytest
from django.utils import timezone

from apps.agenda.disponibilidad import momento_local
from apps.agenda.models import BloqueHorario, ConfiguracionAgenda, EstadoVisita, Visita

pytestmark = pytest.mark.django_db


def url_de(slug):
    return f"/api/t/{slug}/agenda/visitas"


@pytest.fixture
def dia_con_atencion():
    return (timezone.localtime() + timedelta(days=3)).date()


@pytest.fixture
def bloque_a(tienda_a, dia_con_atencion):
    return BloqueHorario.objects.create(
        tienda=tienda_a,
        dia_semana=dia_con_atencion.weekday(),
        hora_inicio=time(10, 0),
        hora_fin=time(11, 0),
    )


@pytest.fixture
def hora(dia_con_atencion):
    """Las 10:00 de ese día, en UTC, que es como viaja por la API."""
    return momento_local(dia_con_atencion, time(10, 0))


def solicitud(**extra):
    datos = {
        "nombreContacto": "Camila Rojas",
        "correoContacto": "camila@ejemplo.cl",
        "telefonoContacto": "+56 9 1234 5678",
    }
    datos.update(extra)
    return datos


def como(client, usuario):
    """Cliente autenticado con el token de ese usuario."""
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


def pedir(client, slug, **extra):
    return client.post(
        url_de(slug), solicitud(**extra), content_type="application/json"
    )


# ── El camino feliz ─────────────────────────────────────────────────────────


def test_la_compradora_pide_una_hora(
    client, comprador, tienda_a, configuracion_a, bloque_a, hora
):
    respuesta = pedir(como(client, comprador), tienda_a.slug, inicio=hora.isoformat())

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == EstadoVisita.SOLICITADA
    assert cuerpo["estadoNombre"] == "Solicitada"
    assert cuerpo["nombreContacto"] == "Camila Rojas"

    visita = Visita.objects.get(uid=cuerpo["uid"])
    assert visita.tienda == tienda_a
    assert visita.comprador == comprador
    assert visita.inicio == hora
    # El término lo pone la duración del bloque, no el navegador.
    assert visita.fin == hora + timedelta(minutes=configuracion_a.duracion_minutos)


def test_un_bloque_que_confirma_solo_deja_la_visita_confirmada(
    client, comprador, tienda_a, configuracion_a, bloque_a, hora
):
    bloque_a.confirmacion_automatica = True
    bloque_a.save()

    respuesta = pedir(como(client, comprador), tienda_a.slug, inicio=hora.isoformat())

    assert respuesta.json()["estado"] == EstadoVisita.CONFIRMADA


def test_la_hora_pedida_deja_de_estar_disponible(
    client, comprador, tienda_a, configuracion_a, bloque_a, hora
):
    pedir(como(client, comprador), tienda_a.slug, inicio=hora.isoformat())

    horas = client.get(f"/api/t/{tienda_a.slug}/agenda/horas").json()["horas"]

    assert hora.isoformat() not in [disponible["inicio"] for disponible in horas]


# ── Quién puede reservar ────────────────────────────────────────────────────


def test_sin_sesion_no_se_puede_reservar(
    client, tienda_a, configuracion_a, bloque_a, hora
):
    assert pedir(client, tienda_a.slug, inicio=hora.isoformat()).status_code == 401


def test_el_dueno_de_una_tienda_no_reserva_visitas(
    client, dueno_a, tienda_a, configuracion_a, bloque_a, hora
):
    """Reservar es de compradores. El dueño administra la agenda, no la ocupa."""
    respuesta = pedir(como(client, dueno_a), tienda_a.slug, inicio=hora.isoformat())

    assert respuesta.status_code == 403


# ── Horas que no se pueden pedir ────────────────────────────────────────────


def test_una_hora_que_la_tienda_no_ofrece_se_rechaza(
    client,
    comprador,
    tienda_a,
    configuracion_a,
    bloque_a,
    dia_con_atencion,
    detalles_de_error,
):
    fuera_del_bloque = momento_local(dia_con_atencion, time(17, 0))

    respuesta = pedir(
        como(client, comprador), tienda_a.slug, inicio=fuera_del_bloque.isoformat()
    )

    assert respuesta.status_code == 400
    assert "inicio" in detalles_de_error(respuesta)


def test_una_hora_sin_la_anticipacion_minima_se_rechaza(
    client, comprador, tienda_a, configuracion_a, detalles_de_error
):
    """La anticipación la impone el backend, aunque el bloque abra hoy."""
    dentro_de_dos_horas = (timezone.localtime() + timedelta(hours=2)).replace(
        minute=0, second=0, microsecond=0
    )
    BloqueHorario.objects.create(
        tienda=tienda_a,
        fecha=dentro_de_dos_horas.date(),
        hora_inicio=time(0, 0),
        hora_fin=time(23, 30),
    )

    respuesta = pedir(
        como(client, comprador), tienda_a.slug, inicio=dentro_de_dos_horas.isoformat()
    )

    assert respuesta.status_code == 400
    assert "inicio" in detalles_de_error(respuesta)


def test_una_hora_ya_llena_se_rechaza(
    client,
    comprador,
    tienda_a,
    configuracion_a,
    bloque_a,
    hora,
    crear_visita,
    detalles_de_error,
):
    crear_visita(tienda_a, inicio=hora, fin=hora + timedelta(minutes=30))

    respuesta = pedir(como(client, comprador), tienda_a.slug, inicio=hora.isoformat())

    assert respuesta.status_code == 400
    assert "inicio" in detalles_de_error(respuesta)


def test_no_se_piden_dos_visitas_a_la_misma_hora(
    client, comprador, tienda_a, configuracion_a, bloque_a, hora, detalles_de_error
):
    """Apretar dos veces el botón es eso, no dos visitas."""
    bloque_a.visitas_simultaneas = 3
    bloque_a.save()
    sesion = como(client, comprador)

    assert pedir(sesion, tienda_a.slug, inicio=hora.isoformat()).status_code == 201

    respuesta = pedir(sesion, tienda_a.slug, inicio=hora.isoformat())
    assert respuesta.status_code == 400
    assert "inicio" in detalles_de_error(respuesta)


def test_una_tienda_inactiva_no_recibe_visitas(
    client, comprador, tienda_a, configuracion_a, bloque_a, hora
):
    tienda_a.activa = False
    tienda_a.save()

    respuesta = pedir(como(client, comprador), tienda_a.slug, inicio=hora.isoformat())

    assert respuesta.status_code == 404


def test_una_tienda_sin_agenda_no_recibe_visitas(client, comprador, tienda_a, hora):
    respuesta = pedir(como(client, comprador), tienda_a.slug, inicio=hora.isoformat())

    assert respuesta.status_code == 404


# ── Aislamiento entre tiendas ───────────────────────────────────────────────


@pytest.mark.aislamiento
def test_una_hora_de_otra_tienda_no_sirve_en_esta(
    client,
    comprador,
    tienda_a,
    tienda_b,
    configuracion_a,
    dia_con_atencion,
    detalles_de_error,
):
    """El bloque es de la tienda B: pedirlo en la A no debe crear nada."""
    ConfiguracionAgenda.objects.create(tienda=tienda_b)
    BloqueHorario.objects.create(
        tienda=tienda_b,
        dia_semana=dia_con_atencion.weekday(),
        hora_inicio=time(15, 0),
        hora_fin=time(16, 0),
    )
    hora_de_b = momento_local(dia_con_atencion, time(15, 0))

    respuesta = pedir(
        como(client, comprador), tienda_a.slug, inicio=hora_de_b.isoformat()
    )

    assert respuesta.status_code == 400
    assert "inicio" in detalles_de_error(respuesta)
    assert not Visita.objects.exists()


@pytest.mark.aislamiento
def test_una_visita_en_otra_tienda_no_ocupa_el_cupo_de_esta(
    client, comprador, tienda_a, tienda_b, configuracion_a, bloque_a, hora, crear_visita
):
    crear_visita(tienda_b, inicio=hora, fin=hora + timedelta(minutes=30))

    respuesta = pedir(como(client, comprador), tienda_a.slug, inicio=hora.isoformat())

    assert respuesta.status_code == 201
    assert Visita.objects.get(tienda=tienda_a).comprador == comprador


@pytest.mark.aislamiento
def test_la_visita_queda_en_la_tienda_de_la_ruta_y_no_en_la_del_cuerpo(
    client, comprador, tienda_a, tienda_b, configuracion_a, bloque_a, hora
):
    """Un `tienda` en el cuerpo no se confía nunca: se ignora."""
    pedir(
        como(client, comprador),
        tienda_a.slug,
        inicio=hora.isoformat(),
        tienda=tienda_b.pk,
    )

    assert Visita.objects.get().tienda == tienda_a
