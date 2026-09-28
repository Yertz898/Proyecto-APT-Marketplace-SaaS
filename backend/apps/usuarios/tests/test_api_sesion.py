"""Inicio de sesión, registro de compradores y quién soy."""

import pytest

from apps.usuarios.models import Rol, Usuario
from apps.usuarios.views import AMBITO_AUTENTICACION as AMBITO

pytestmark = pytest.mark.django_db

SESION = "/api/auth/sesion"
RENOVAR = "/api/auth/sesion/renovar"
REGISTRO = "/api/auth/registro"
YO = "/api/auth/yo"

CLAVE = "clave-de-prueba"


def entrar(client, usuario, clave=CLAVE):
    return client.post(
        SESION,
        {"email": usuario.email, "password": clave},
        content_type="application/json",
    )


# ── Inicio de sesión ────────────────────────────────────────────────────────


def test_entrega_los_dos_tokens_y_quien_inicio_sesion(client, dueno_a, tienda_a):
    respuesta = entrar(client, dueno_a)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["access"] and cuerpo["refresh"]
    assert cuerpo["usuario"]["email"] == dueno_a.email
    assert cuerpo["usuario"]["rol"] == Rol.DUENO_TIENDA
    assert cuerpo["usuario"]["tienda"] == {
        "slug": tienda_a.slug,
        "nombre": tienda_a.nombre,
    }


def test_el_comprador_no_tiene_tienda_en_la_sesion(client, comprador):
    assert entrar(client, comprador).json()["usuario"]["tienda"] is None


def test_la_respuesta_nunca_trae_la_contrasena(client, dueno_a):
    assert "password" not in entrar(client, dueno_a).json()["usuario"]


def test_una_contrasena_equivocada_no_deja_entrar(client, dueno_a):
    assert entrar(client, dueno_a, clave="otra-cosa").status_code == 401


def test_un_correo_que_no_existe_no_deja_entrar(client, db):
    respuesta = client.post(
        SESION,
        {"email": "nadie@ejemplo.cl", "password": CLAVE},
        content_type="application/json",
    )

    assert respuesta.status_code == 401


def test_una_cuenta_desactivada_no_deja_entrar(client, dueno_a):
    dueno_a.is_active = False
    dueno_a.save()

    assert entrar(client, dueno_a).status_code == 401


def test_el_token_lleva_el_rol_y_la_tienda(client, dueno_a, tienda_a):
    from rest_framework_simplejwt.tokens import AccessToken

    token = AccessToken(entrar(client, dueno_a).json()["access"])

    assert token["rol"] == Rol.DUENO_TIENDA
    assert token["tienda"] == tienda_a.slug


def test_el_token_de_refresco_renueva_el_de_acceso(client, comprador):
    refresco = entrar(client, comprador).json()["refresh"]

    respuesta = client.post(
        RENOVAR, {"refresh": refresco}, content_type="application/json"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["access"]


def test_el_inicio_de_sesion_corta_los_intentos_a_ciegas(client, monkeypatch, dueno_a):
    """
    Probar contraseñas contra el endpoint no puede salir gratis.

    La tasa se cambia sobre la clase y no con `settings`: DRF fija
    `THROTTLE_RATES` al importar el módulo, así que tocar la configuración
    después no la mueve. Lo que se prueba igual es lo que importa: que la vista
    declara el ámbito y que el límite se aplica.
    """
    from rest_framework.throttling import ScopedRateThrottle

    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {AMBITO: "3/min"}, raising=False
    )

    for _ in range(3):
        assert entrar(client, dueno_a, clave="adivinando").status_code == 401

    assert entrar(client, dueno_a, clave="adivinando").status_code == 429


def test_el_registro_comparte_el_limite_de_intentos(client, monkeypatch, db):
    from rest_framework.throttling import ScopedRateThrottle

    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {AMBITO: "2/min"}, raising=False
    )

    registrar(client)
    registrar(client, email="otra@ejemplo.cl")

    assert registrar(client, email="tercera@ejemplo.cl").status_code == 429


def test_el_limite_configurado_es_el_que_se_aplica(settings):
    """La tasa sale de la configuración, no de un número escrito en el código."""
    from rest_framework.throttling import ScopedRateThrottle

    assert (
        ScopedRateThrottle.THROTTLE_RATES[AMBITO]
        == (settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"][AMBITO])
    )


# ── Registro de compradores ─────────────────────────────────────────────────


def datos_de_registro(**extra):
    datos = {
        "nombre": "Camila Rojas",
        "email": "camila@ejemplo.cl",
        "password": "una-clave-larga-97",
    }
    datos.update(extra)
    return datos


def registrar(client, **extra):
    return client.post(
        REGISTRO, datos_de_registro(**extra), content_type="application/json"
    )


def test_crea_la_cuenta_como_compradora(client, db):
    respuesta = registrar(client)

    assert respuesta.status_code == 201
    cuenta = Usuario.objects.get(email="camila@ejemplo.cl")
    assert cuenta.rol == Rol.COMPRADOR
    assert cuenta.tienda_id is None
    assert cuenta.check_password("una-clave-larga-97")


def test_la_respuesta_del_registro_no_devuelve_la_contrasena(client, db):
    assert "password" not in registrar(client).json()


def test_no_se_puede_registrar_con_otro_rol(client, tienda_a):
    """Mandar el rol en el cuerpo no sirve de nada: siempre queda comprador."""
    respuesta = registrar(client, rol=Rol.ADMIN_PLATAFORMA, tienda=tienda_a.pk)

    assert respuesta.status_code == 201
    cuenta = Usuario.objects.get(email="camila@ejemplo.cl")
    assert cuenta.rol == Rol.COMPRADOR
    assert cuenta.tienda_id is None
    assert cuenta.is_staff is False
    assert cuenta.is_superuser is False


def test_un_correo_repetido_se_rechaza(client, comprador, detalles_de_error):
    respuesta = registrar(client, email=comprador.email)

    assert respuesta.status_code == 400
    assert "email" in detalles_de_error(respuesta)


def test_un_correo_repetido_con_otras_mayusculas_tambien_se_rechaza(
    client, comprador, detalles_de_error
):
    respuesta = registrar(client, email=comprador.email.upper())

    assert respuesta.status_code == 400
    assert "email" in detalles_de_error(respuesta)


def test_una_contrasena_debil_se_rechaza(client, db, detalles_de_error):
    respuesta = registrar(client, password="12345")

    assert respuesta.status_code == 400
    assert "password" in detalles_de_error(respuesta)


def test_dos_cuentas_sin_rut_conviven(client, db):
    assert registrar(client).status_code == 201
    assert registrar(client, email="otra@ejemplo.cl").status_code == 201


def test_el_rut_se_guarda_normalizado(client, db):
    assert registrar(client, rut="12.345.678-5").status_code == 201

    assert Usuario.objects.get(email="camila@ejemplo.cl").rut == "12345678-5"


def test_un_rut_invalido_se_rechaza(client, db, detalles_de_error):
    respuesta = registrar(client, rut="12345678-9")

    assert respuesta.status_code == 400
    assert "rut" in detalles_de_error(respuesta)


def test_un_rut_repetido_con_otro_formato_se_rechaza(client, db, detalles_de_error):
    registrar(client, rut="12345678-5")

    respuesta = registrar(client, email="otra@ejemplo.cl", rut="12.345.678-5")

    assert respuesta.status_code == 400
    assert "rut" in detalles_de_error(respuesta)


# ── Quién soy ───────────────────────────────────────────────────────────────


def test_sin_sesion_no_dice_quien_soy(client, db):
    assert client.get(YO).status_code == 401


def test_con_un_token_inventado_no_dice_quien_soy(client, db):
    assert client.get(YO, HTTP_AUTHORIZATION="Bearer no-es-un-token").status_code == 401


def test_dice_quien_soy_y_en_que_tienda_trabajo(client, vendedor_b, tienda_b):
    acceso = entrar(client, vendedor_b).json()["access"]

    cuerpo = client.get(YO, HTTP_AUTHORIZATION=f"Bearer {acceso}").json()

    assert cuerpo["email"] == vendedor_b.email
    assert cuerpo["rol"] == Rol.VENDEDOR
    assert cuerpo["rolNombre"] == "Vendedor"
    assert cuerpo["tienda"]["slug"] == tienda_b.slug
