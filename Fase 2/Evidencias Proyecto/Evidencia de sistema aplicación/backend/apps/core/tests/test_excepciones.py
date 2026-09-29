"""El formato único de error de la API."""

import pytest

pytestmark = pytest.mark.django_db


def error_de(respuesta):
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"error"}
    assert set(cuerpo["error"]) == {"codigo", "mensaje", "detalles"}
    return cuerpo["error"]


def test_un_campo_invalido_llega_como_validacion(client, tienda_a, configuracion_a):
    respuesta = client.get(
        f"/api/t/{tienda_a.slug}/agenda/horas", {"desde": "05-10-2026"}
    )

    error = error_de(respuesta)
    assert respuesta.status_code == 400
    assert error["codigo"] == "validacion"
    assert error["detalles"]["desde"] == ["Usa el formato aaaa-mm-dd."]


def test_sin_sesion_el_codigo_dice_que_falta_la_sesion(client, db):
    error = error_de(client.get("/api/auth/yo"))

    assert error["codigo"] == "sin_sesion"
    assert error["mensaje"] == "Inicia sesión para continuar."


def test_credenciales_malas_no_dicen_cual_de_las_dos_falló(client, dueno_a):
    respuesta = client.post(
        "/api/auth/sesion",
        {"email": dueno_a.email, "password": "otra-cosa"},
        content_type="application/json",
    )

    error = error_de(respuesta)
    assert respuesta.status_code == 401
    assert error["codigo"] == "credenciales_invalidas"
    # El mismo texto para correo inexistente y contraseña mala: distinguirlos
    # sirve para averiguar qué correos tienen cuenta.
    assert error["mensaje"] == "El correo o la contraseña no coinciden."


def test_un_correo_que_no_existe_da_el_mismo_mensaje(client, db):
    respuesta = client.post(
        "/api/auth/sesion",
        {"email": "nadie@ejemplo.cl", "password": "lo-que-sea"},
        content_type="application/json",
    )

    assert error_de(respuesta)["mensaje"] == "El correo o la contraseña no coinciden."


def test_una_tienda_que_no_existe_no_confirma_nada(client, db):
    error = error_de(client.get("/api/t/no-existe/agenda/horas"))

    assert error["codigo"] == "no_encontrado"
    assert error["mensaje"] == "No encontramos lo que buscas."
    assert error["detalles"] == {}


def test_el_mensaje_que_escribe_la_vista_es_el_que_se_muestra(client, tienda_a):
    """La agenda sin configurar dice algo más útil que el genérico."""
    error = error_de(client.get(f"/api/t/{tienda_a.slug}/agenda/horas"))

    assert error["codigo"] == "no_encontrado"
    assert error["mensaje"] == "Esta tienda no recibe visitas con hora."


def test_demasiados_intentos_dice_cuánto_esperar(client, monkeypatch, dueno_a):
    from rest_framework.throttling import ScopedRateThrottle

    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {"autenticacion": "1/min"}, raising=False
    )

    credenciales = {"email": dueno_a.email, "password": "mal"}
    client.post("/api/auth/sesion", credenciales, content_type="application/json")
    respuesta = client.post(
        "/api/auth/sesion", credenciales, content_type="application/json"
    )

    error = error_de(respuesta)
    assert respuesta.status_code == 429
    assert error["codigo"] == "demasiados_intentos"
    assert error["detalles"]["segundos"] > 0


def test_un_error_nunca_trae_trazas_ni_rutas(client, tienda_a, configuracion_a):
    cuerpo = client.get(
        f"/api/t/{tienda_a.slug}/agenda/horas", {"dias": "muchos"}
    ).content.decode()

    for filtracion in ("Traceback", "/app/", "apps.agenda", "SELECT"):
        assert filtracion not in cuerpo
