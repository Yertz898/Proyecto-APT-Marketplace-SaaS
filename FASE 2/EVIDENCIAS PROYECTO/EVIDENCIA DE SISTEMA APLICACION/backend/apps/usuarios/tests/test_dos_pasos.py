"""
Verificación en dos pasos (Google Authenticator) para dueños y administración.

Lo que no puede fallar: sin activarla, entrar funciona igual que antes; con
ella activa, la contraseña sola no entrega tokens; un código malo, un desafío
vencido o un código de respaldo ya usado no sirven; y un comprador no puede
activarla.
"""

import pyotp
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.usuarios import dos_pasos

pytestmark = pytest.mark.django_db

CLAVE = "clave-de-prueba"


def anonimo():
    return APIClient(SERVER_NAME="localhost")


def como(usuario):
    cliente = APIClient(SERVER_NAME="localhost")
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(usuario)}")
    return cliente


def entrar(usuario):
    return anonimo().post(
        "/api/auth/sesion", {"email": usuario.email, "password": CLAVE}, format="json"
    )


def activar(usuario) -> tuple[str, list[str]]:
    """Activa la verificación como lo haría la pantalla. Devuelve secreto y respaldo."""
    cliente = como(usuario)
    secreto = cliente.post("/api/auth/otp/iniciar").json()["secreto"]
    respuesta = cliente.post(
        "/api/auth/otp/confirmar", {"codigo": pyotp.TOTP(secreto).now()}, format="json"
    )
    assert respuesta.status_code == 200, respuesta.json()
    return secreto, respuesta.json()["codigosDeRespaldo"]


def test_sin_activarla_se_entra_como_siempre(dueno_a):
    respuesta = entrar(dueno_a)

    assert respuesta.status_code == 200
    assert "access" in respuesta.json()


def test_activarla_entrega_qr_y_codigos_de_respaldo(dueno_a):
    cliente = como(dueno_a)
    inicio = cliente.post("/api/auth/otp/iniciar").json()

    assert inicio["qr"].startswith("data:image/svg+xml;base64,")
    dueno_a.refresh_from_db()
    assert not dueno_a.otp_activo  # todavía falta confirmar

    _, respaldo = activar(dueno_a)

    dueno_a.refresh_from_db()
    assert dueno_a.otp_activo
    assert len(respaldo) == 8
    # Se guardan huellas, no los códigos.
    assert respaldo[0] not in str(dueno_a.otp_respaldo)


def test_con_la_verificacion_activa_la_contrasena_sola_no_entrega_tokens(dueno_a):
    secreto, _ = activar(dueno_a)

    primero = entrar(dueno_a).json()

    assert primero["otpRequerido"] is True
    assert "access" not in primero

    # El código de la activación se anota aparte: el mismo sirve para entrar.
    codigo = pyotp.TOTP(secreto).now()
    segundo = anonimo().post(
        "/api/auth/sesion/otp",
        {"desafio": primero["desafio"], "codigo": codigo},
        format="json",
    )
    assert segundo.status_code == 200, segundo.json()
    assert "access" in segundo.json()
    assert segundo.json()["usuario"]["email"] == dueno_a.email


def test_un_codigo_malo_no_entra(dueno_a):
    activar(dueno_a)
    desafio = entrar(dueno_a).json()["desafio"]

    respuesta = anonimo().post(
        "/api/auth/sesion/otp", {"desafio": desafio, "codigo": "000000"}, format="json"
    )

    assert respuesta.status_code == 400
    assert "access" not in respuesta.json()


def test_un_desafio_inventado_o_vencido_no_sirve(dueno_a, monkeypatch):
    secreto, _ = activar(dueno_a)
    codigo = pyotp.TOTP(secreto).now()

    falso = anonimo().post(
        "/api/auth/sesion/otp",
        {"desafio": "inventado", "codigo": codigo},
        format="json",
    )
    assert falso.status_code == 400

    desafio = dos_pasos.crear_desafio(dueno_a)
    monkeypatch.setattr(dos_pasos, "VIGENCIA_DEL_DESAFIO", -1)
    vencido = anonimo().post(
        "/api/auth/sesion/otp", {"desafio": desafio, "codigo": codigo}, format="json"
    )
    assert vencido.status_code == 400


def test_un_codigo_de_respaldo_sirve_una_sola_vez(dueno_a):
    _, respaldo = activar(dueno_a)

    def con_respaldo():
        desafio = entrar(dueno_a).json()["desafio"]
        return anonimo().post(
            "/api/auth/sesion/otp",
            {"desafio": desafio, "codigo": respaldo[0]},
            format="json",
        )

    assert con_respaldo().status_code == 200
    assert con_respaldo().status_code == 400


def test_despues_de_cinco_codigos_malos_hay_que_esperar(dueno_a):
    secreto, _ = activar(dueno_a)
    desafio = entrar(dueno_a).json()["desafio"]
    for _ in range(dos_pasos.MAXIMO_DE_FALLOS):
        anonimo().post(
            "/api/auth/sesion/otp",
            {"desafio": desafio, "codigo": "111111"},
            format="json",
        )

    respuesta = anonimo().post(
        "/api/auth/sesion/otp",
        {"desafio": desafio, "codigo": pyotp.TOTP(secreto).now()},
        format="json",
    )

    assert respuesta.status_code == 429


def test_desactivar_pide_contrasena_y_codigo(dueno_a):
    _, respaldo = activar(dueno_a)
    cliente = como(dueno_a)

    sin_clave = cliente.post(
        "/api/auth/otp/desactivar",
        {"password": "otra", "codigo": respaldo[0]},
        format="json",
    )
    assert sin_clave.status_code == 400

    bien = cliente.post(
        "/api/auth/otp/desactivar",
        {"password": CLAVE, "codigo": respaldo[1]},
        format="json",
    )
    assert bien.status_code == 204
    dueno_a.refresh_from_db()
    assert not dueno_a.otp_activo
    assert "access" in entrar(dueno_a).json()


def test_la_administracion_tambien_puede_activarla(admin_plataforma):
    activar(admin_plataforma)

    assert entrar(admin_plataforma).json()["otpRequerido"] is True


def test_un_comprador_no_puede_activarla(comprador):
    respuesta = como(comprador).post("/api/auth/otp/iniciar")

    assert respuesta.status_code == 403
