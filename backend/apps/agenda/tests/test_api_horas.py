"""Endpoint público de horas disponibles."""

from datetime import date, time, timedelta

import pytest
from django.utils import timezone

from apps.agenda.models import BloqueHorario, ConfiguracionAgenda

pytestmark = pytest.mark.django_db


def url_de(slug):
    return f"/api/t/{slug}/agenda/horas"


@pytest.fixture
def dia_con_atencion():
    """Un día dentro de la ventana y más allá de la anticipación mínima."""
    return (timezone.localtime() + timedelta(days=3)).date()


def abrir_atencion(tienda, dia, inicio=time(10, 0), fin=time(13, 0), **extra):
    datos = {
        "tienda": tienda,
        "dia_semana": dia.weekday(),
        "hora_inicio": inicio,
        "hora_fin": fin,
    }
    datos.update(extra)
    return BloqueHorario.objects.create(**datos)


def test_entrega_las_horas_de_la_tienda(
    client, tienda_a, configuracion_a, dia_con_atencion
):
    abrir_atencion(tienda_a, dia_con_atencion)

    respuesta = client.get(
        url_de(tienda_a.slug), {"desde": dia_con_atencion, "hasta": dia_con_atencion}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["direccion"] == configuracion_a.direccion
    assert (
        cuerpo["anticipacionMinimaHoras"] == configuracion_a.anticipacion_minima_horas
    )
    assert len(cuerpo["horas"]) == 6

    primera = cuerpo["horas"][0]
    assert set(primera) == {
        "inicio",
        "fin",
        "bloqueId",
        "nombreBloque",
        "cuposLibres",
        "confirmacionAutomatica",
    }
    assert primera["cuposLibres"] == 1
    assert primera["confirmacionAutomatica"] is False


def test_no_necesita_sesion(client, tienda_a, configuracion_a):
    assert client.get(url_de(tienda_a.slug)).status_code == 200


def test_una_tienda_sin_agenda_configurada_responde_404(client, tienda_a):
    assert client.get(url_de(tienda_a.slug)).status_code == 404


def test_una_tienda_inactiva_responde_404(client, tienda_a, configuracion_a):
    tienda_a.activa = False
    tienda_a.save()

    assert client.get(url_de(tienda_a.slug)).status_code == 404


def test_una_fecha_mal_escrita_es_error_de_peticion(client, tienda_a, configuracion_a):
    respuesta = client.get(url_de(tienda_a.slug), {"desde": "05-10-2026"})

    assert respuesta.status_code == 400
    assert "desde" in respuesta.json()


def test_el_rango_acota_los_dias(client, tienda_a, configuracion_a, dia_con_atencion):
    abrir_atencion(tienda_a, dia_con_atencion)
    otro_dia = dia_con_atencion + timedelta(days=1)

    respuesta = client.get(
        url_de(tienda_a.slug), {"desde": otro_dia, "hasta": otro_dia}
    )

    assert respuesta.json()["horas"] == []


def test_un_bloque_con_su_propia_duracion_se_refleja_en_las_horas(
    client, tienda_a, configuracion_a, dia_con_atencion
):
    abrir_atencion(tienda_a, dia_con_atencion, fin=time(12, 0), duracion_minutos=60)

    horas = client.get(
        url_de(tienda_a.slug), {"desde": dia_con_atencion, "hasta": dia_con_atencion}
    ).json()["horas"]

    assert len(horas) == 2


@pytest.mark.aislamiento
def test_las_horas_de_una_tienda_no_incluyen_bloques_de_otra(
    client, tienda_a, tienda_b, configuracion_a, dia_con_atencion
):
    ConfiguracionAgenda.objects.create(tienda=tienda_b)
    abrir_atencion(tienda_a, dia_con_atencion, inicio=time(10, 0), fin=time(11, 0))
    abrir_atencion(tienda_b, dia_con_atencion, inicio=time(15, 0), fin=time(18, 0))

    horas = client.get(
        url_de(tienda_a.slug), {"desde": dia_con_atencion, "hasta": dia_con_atencion}
    ).json()["horas"]

    assert len(horas) == 2
    assert all(hora["inicio"] < f"{dia_con_atencion}T14" for hora in horas)


@pytest.mark.aislamiento
def test_las_visitas_de_otra_tienda_no_ocupan_cupo(
    client, tienda_a, tienda_b, configuracion_a, dia_con_atencion, crear_visita
):
    abrir_atencion(tienda_a, dia_con_atencion, inicio=time(10, 0), fin=time(10, 30))

    from apps.agenda.disponibilidad import momento_local

    inicio = momento_local(dia_con_atencion, time(10, 0))
    crear_visita(tienda_b, inicio=inicio, fin=inicio + timedelta(minutes=30))

    horas = client.get(
        url_de(tienda_a.slug), {"desde": dia_con_atencion, "hasta": dia_con_atencion}
    ).json()["horas"]

    assert len(horas) == 1
    assert horas[0]["cuposLibres"] == 1


def test_un_dia_sin_bloques_no_trae_horas(client, tienda_a, configuracion_a):
    assert (
        client.get(url_de(tienda_a.slug), {"desde": date(2030, 1, 1)}).json()["horas"]
        == []
    )
