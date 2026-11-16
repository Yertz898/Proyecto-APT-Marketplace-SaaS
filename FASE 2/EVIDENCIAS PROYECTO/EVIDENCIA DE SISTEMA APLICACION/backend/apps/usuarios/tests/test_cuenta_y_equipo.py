"""La cuenta propia y el equipo de la tienda."""

import pytest
from rest_framework.test import APIClient

from apps.tiendas.models import Plan
from apps.usuarios.models import Rol, Usuario

pytestmark = pytest.mark.django_db

CLAVE = "clave-de-prueba"
CLAVE_NUEVA = "Otra-Clave-Segura-2026"


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


# ── Cuenta propia ───────────────────────────────────────────────────────────


def test_cambia_su_nombre(dueno_a):
    respuesta = como(dueno_a).patch(
        "/api/auth/yo", {"nombre": "Ana Dueña"}, format="json"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Ana Dueña"
    dueno_a.refresh_from_db()
    assert dueno_a.nombre == "Ana Dueña"


def test_no_puede_cambiarse_el_rol_por_la_cuenta(comprador):
    como(comprador).patch("/api/auth/yo", {"rol": Rol.ADMIN_PLATAFORMA}, format="json")

    comprador.refresh_from_db()
    assert comprador.rol == Rol.COMPRADOR


def test_cambia_su_contrasena_con_la_actual(dueno_a):
    respuesta = como(dueno_a).post(
        "/api/auth/contrasena", {"actual": CLAVE, "nueva": CLAVE_NUEVA}, format="json"
    )

    assert respuesta.status_code == 204
    dueno_a.refresh_from_db()
    assert dueno_a.check_password(CLAVE_NUEVA)


def test_sin_la_contrasena_actual_no_la_cambia(dueno_a, detalles_de_error):
    respuesta = como(dueno_a).post(
        "/api/auth/contrasena",
        {"actual": "equivocada", "nueva": CLAVE_NUEVA},
        format="json",
    )

    assert respuesta.status_code == 400
    assert "actual" in detalles_de_error(respuesta)
    dueno_a.refresh_from_db()
    assert dueno_a.check_password(CLAVE)


def test_una_contrasena_debil_se_rechaza(dueno_a):
    respuesta = como(dueno_a).post(
        "/api/auth/contrasena", {"actual": CLAVE, "nueva": "123"}, format="json"
    )

    assert respuesta.status_code == 400


# ── Equipo ──────────────────────────────────────────────────────────────────


def test_el_dueno_ve_solo_su_equipo(premium, dueno_a, dueno_b, vendedor_b):
    respuesta = como(dueno_b).get("/api/panel/equipo")

    assert respuesta.status_code == 200
    correos = {m["email"] for m in respuesta.json()}
    assert correos == {dueno_b.email, vendedor_b.email}


def test_el_dueno_crea_un_vendedor_en_su_tienda(premium, dueno_a, tienda_a):
    respuesta = como(dueno_a).post(
        "/api/panel/equipo",
        {"nombre": "Vendedora", "email": "vende@ejemplo.cl", "password": CLAVE_NUEVA},
        format="json",
    )

    assert respuesta.status_code == 201
    nuevo = Usuario.objects.get(email="vende@ejemplo.cl")
    assert nuevo.rol == Rol.VENDEDOR
    assert nuevo.tienda == tienda_a


def test_un_vendedor_no_administra_el_equipo(premium, vendedor_b):
    assert como(vendedor_b).get("/api/panel/equipo").status_code == 403


def test_el_plan_basico_no_tiene_equipo(dueno_a):
    assert como(dueno_a).get("/api/panel/equipo").status_code == 403


def test_no_se_toca_a_un_vendedor_de_otra_tienda(premium, dueno_a, vendedor_b):
    cliente = como(dueno_a)

    assert (
        cliente.patch(
            f"/api/panel/equipo/{vendedor_b.pk}", {"activo": False}, format="json"
        ).status_code
        == 404
    )
    assert (
        cliente.post(
            f"/api/panel/equipo/{vendedor_b.pk}/contrasena",
            {"nueva": CLAVE_NUEVA},
            format="json",
        ).status_code
        == 404
    )
    vendedor_b.refresh_from_db()
    assert vendedor_b.is_active


def test_el_dueno_desactiva_y_reinicia_la_clave_de_su_vendedor(
    premium, dueno_b, vendedor_b
):
    cliente = como(dueno_b)

    assert (
        cliente.patch(
            f"/api/panel/equipo/{vendedor_b.pk}", {"activo": False}, format="json"
        ).status_code
        == 200
    )
    assert (
        cliente.post(
            f"/api/panel/equipo/{vendedor_b.pk}/contrasena",
            {"nueva": CLAVE_NUEVA},
            format="json",
        ).status_code
        == 204
    )
    vendedor_b.refresh_from_db()
    assert not vendedor_b.is_active
    assert vendedor_b.check_password(CLAVE_NUEVA)


def test_el_dueno_no_se_desactiva_a_si_mismo(premium, dueno_b):
    respuesta = como(dueno_b).patch(
        f"/api/panel/equipo/{dueno_b.pk}", {"activo": False}, format="json"
    )

    assert respuesta.status_code == 400
    dueno_b.refresh_from_db()
    assert dueno_b.is_active
