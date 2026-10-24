"""Solicitudes de acceso desde la portada: POST /api/solicitudes-de-acceso."""

import pytest

from apps.tiendas.models import EstadoSolicitud, SolicitudDeAcceso

pytestmark = pytest.mark.django_db

URL = "/api/solicitudes-de-acceso"


def datos(**extra):
    base = {
        "negocio": "Distribuidora Los Andes",
        "nombre": "Rodrigo Pérez",
        "email": "contacto@losandes.cl",
        "telefono": "+56 9 1234 5678",
    }
    base.update(extra)
    return base


def pedir(client, **extra):
    return client.post(URL, datos(**extra), content_type="application/json")


def test_guarda_la_solicitud(client, db):
    respuesta = pedir(client, mensaje="Vendemos abarrotes al por mayor.")

    assert respuesta.status_code == 201
    solicitud = SolicitudDeAcceso.objects.get()
    assert solicitud.negocio == "Distribuidora Los Andes"
    assert solicitud.mensaje == "Vendemos abarrotes al por mayor."
    # Llega como nueva: el equipo la mueve desde el panel de administración.
    assert solicitud.estado == EstadoSolicitud.NUEVA


def test_no_necesita_sesion(client, db):
    assert pedir(client).status_code == 201


def test_el_mensaje_es_opcional(client, db):
    assert pedir(client).status_code == 201
    assert SolicitudDeAcceso.objects.get().mensaje == ""


@pytest.mark.parametrize("campo", ["negocio", "nombre", "email", "telefono"])
def test_los_campos_obligatorios_se_exigen(client, db, detalles_de_error, campo):
    respuesta = client.post(
        URL,
        {clave: valor for clave, valor in datos().items() if clave != campo},
        content_type="application/json",
    )

    assert respuesta.status_code == 400
    assert campo in detalles_de_error(respuesta)


def test_un_correo_mal_escrito_se_rechaza(client, db, detalles_de_error):
    respuesta = pedir(client, email="no-es-un-correo")

    assert respuesta.status_code == 400
    assert "email" in detalles_de_error(respuesta)


def test_el_mismo_correo_no_llena_la_bandeja_de_duplicados(
    client, db, detalles_de_error
):
    pedir(client)

    respuesta = pedir(client, negocio="Otro nombre")

    assert respuesta.status_code == 400
    assert "email" in detalles_de_error(respuesta)
    assert SolicitudDeAcceso.objects.count() == 1


def test_el_correo_se_guarda_en_minusculas(client, db):
    pedir(client, email="Contacto@LosAndes.CL")

    assert SolicitudDeAcceso.objects.get().email == "contacto@losandes.cl"


def test_el_mismo_correo_con_otras_mayusculas_tambien_es_duplicado(client, db):
    pedir(client)

    assert pedir(client, email="CONTACTO@LOSANDES.CL").status_code == 400
    assert SolicitudDeAcceso.objects.count() == 1


def test_el_estado_no_se_puede_fijar_desde_el_formulario(client, db):
    """Mandar `estado` o `notas` en el cuerpo no sirve de nada."""
    pedir(client, estado=EstadoSolicitud.ACTIVADA, notas="me activo solo")

    solicitud = SolicitudDeAcceso.objects.get()
    assert solicitud.estado == EstadoSolicitud.NUEVA
    assert solicitud.notas == ""


def test_la_respuesta_no_devuelve_nada_interno(client, db):
    cuerpo = pedir(client).json()

    assert set(cuerpo) == {"negocio", "nombre", "email", "telefono", "mensaje"}


def test_el_formulario_corta_el_envio_repetido(client, monkeypatch, db):
    """Es un formulario público: no puede ser gratis llenar la bandeja."""
    from rest_framework.throttling import ScopedRateThrottle

    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {"solicitudes": "2/hour"}, raising=False
    )

    pedir(client, email="una@ejemplo.cl")
    pedir(client, email="otra@ejemplo.cl")

    assert pedir(client, email="tercera@ejemplo.cl").status_code == 429
    assert SolicitudDeAcceso.objects.count() == 2


def test_el_limite_configurado_es_el_que_se_aplica(settings):
    from rest_framework.throttling import ScopedRateThrottle

    assert (
        ScopedRateThrottle.THROTTLE_RATES["solicitudes"]
        == (settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["solicitudes"])
    )
