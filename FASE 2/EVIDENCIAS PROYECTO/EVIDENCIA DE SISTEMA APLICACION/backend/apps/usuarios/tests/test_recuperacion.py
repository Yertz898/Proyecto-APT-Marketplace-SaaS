"""«¿Olvidaste tu contraseña?»: el enlace por correo y la contraseña nueva."""

import re

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

CLAVE_NUEVA = "Otra-Clave-Segura-2026"


@pytest.fixture(autouse=True)
def correo_local(settings):
    settings.RESEND_API_KEY = ""
    settings.FRONTEND_URL = "https://vitrina.test"


def pedir(email, tienda=""):
    return APIClient().post(
        "/api/auth/contrasena/olvido", {"email": email, "tienda": tienda}, format="json"
    )


def enlace(correo):
    return re.search(r"https://vitrina\.test\S+", correo.body).group(0)


def partes(url):
    uid = re.search(r"uid=([^&]+)", url).group(1)
    token = re.search(r"token=([^&\s]+)", url).group(1)
    return uid, token


def restablecer(uid, token, password=CLAVE_NUEVA):
    return APIClient().post(
        "/api/auth/contrasena/restablecer",
        {"uid": uid, "token": token, "password": password},
        format="json",
    )


def test_el_comprador_recibe_un_enlace_que_vuelve_a_la_tienda(
    comprador, tienda_a, mailoutbox
):
    respuesta = pedir(comprador.email, tienda_a.slug)

    assert respuesta.status_code == 200
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [comprador.email]
    assert f"/t/{tienda_a.slug}/restablecer?uid=" in enlace(mailoutbox[0])


def test_el_dueno_recibe_un_enlace_al_acceso_de_dealcommerce(dueno_a, mailoutbox):
    pedir(dueno_a.email)

    assert "/panel/restablecer?uid=" in enlace(mailoutbox[0])


def test_no_revela_si_el_correo_tiene_cuenta(comprador, mailoutbox):
    con_cuenta = pedir(comprador.email)
    sin_cuenta = pedir("nadie@ejemplo.cl")

    assert sin_cuenta.status_code == 200
    assert sin_cuenta.json() == con_cuenta.json()
    assert len(mailoutbox) == 1


def test_una_tienda_cerrada_no_se_usa_para_el_enlace(comprador, tienda_a, mailoutbox):
    tienda_a.activa = False
    tienda_a.save()

    pedir(comprador.email, tienda_a.slug)

    assert "/panel/restablecer?uid=" in enlace(mailoutbox[0])


def test_el_enlace_cambia_la_contrasena_y_sirve_una_sola_vez(comprador, mailoutbox):
    pedir(comprador.email)
    uid, token = partes(enlace(mailoutbox[0]))

    primera = restablecer(uid, token)
    assert primera.status_code == 200
    comprador.refresh_from_db()
    assert comprador.check_password(CLAVE_NUEVA)

    segunda = restablecer(uid, token, "Una-Tercera-Clave-2026")
    assert segunda.status_code == 400
    assert segunda.json()["error"]["detalles"]["general"]


def test_un_token_inventado_no_sirve(comprador, mailoutbox):
    pedir(comprador.email)
    uid, _ = partes(enlace(mailoutbox[0]))

    respuesta = restablecer(uid, "token-inventado")

    assert respuesta.status_code == 400
    comprador.refresh_from_db()
    assert not comprador.check_password(CLAVE_NUEVA)


def test_la_contrasena_nueva_pasa_por_las_reglas(comprador, mailoutbox):
    pedir(comprador.email)
    uid, token = partes(enlace(mailoutbox[0]))

    respuesta = restablecer(uid, token, "123")

    assert respuesta.status_code == 400
    assert "password" in respuesta.json()["error"]["detalles"]
