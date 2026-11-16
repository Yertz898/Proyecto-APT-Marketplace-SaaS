"""El plan de la tienda y la administración de la plataforma."""

import pytest
from rest_framework.test import APIClient

from apps.auditoria.models import Accion, Registro
from apps.tiendas.models import Plan, Tienda
from apps.usuarios.models import Rol, Usuario

pytestmark = pytest.mark.django_db


def como(usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(usuario)}")
    return cliente


# ── Plan ────────────────────────────────────────────────────────────────────


def test_el_dueno_cambia_de_plan_y_queda_registrado(dueno_a, tienda_a):
    respuesta = como(dueno_a).patch(
        "/api/panel/plan", {"plan": Plan.ULTIMATE}, format="json"
    )

    assert respuesta.status_code == 200
    tienda_a.refresh_from_db()
    assert tienda_a.plan == Plan.ULTIMATE
    assert Registro.objects.filter(tienda=tienda_a, accion=Accion.PLAN).exists()


def test_un_vendedor_no_cambia_el_plan(vendedor_b, tienda_b):
    respuesta = como(vendedor_b).patch(
        "/api/panel/plan", {"plan": Plan.ULTIMATE}, format="json"
    )

    assert respuesta.status_code == 403
    tienda_b.refresh_from_db()
    assert tienda_b.plan == Plan.BASICO


def test_cancelar_cierra_la_vitrina_y_reanudar_la_abre(dueno_a, tienda_a, client):
    cliente = como(dueno_a)

    assert cliente.post("/api/panel/plan/cancelar").status_code == 200
    tienda_a.refresh_from_db()
    assert tienda_a.cancelada_en is not None
    assert not tienda_a.activa
    assert client.get(f"/api/t/{tienda_a.slug}/tienda").status_code == 404

    assert (
        cliente.patch(
            "/api/panel/plan", {"plan": Plan.PREMIUM}, format="json"
        ).status_code
        == 400
    )

    assert cliente.post("/api/panel/plan/reanudar").status_code == 200
    tienda_a.refresh_from_db()
    assert tienda_a.cancelada_en is None
    assert tienda_a.activa


# ── Plataforma ──────────────────────────────────────────────────────────────


def test_solo_el_admin_entra_a_la_plataforma(dueno_a, comprador):
    for usuario in (dueno_a, comprador):
        cliente = como(usuario)
        assert cliente.get("/api/plataforma/tiendas").status_code == 403
        assert cliente.get("/api/plataforma/registros").status_code == 403


def test_el_admin_ve_todas_las_tiendas(admin_plataforma, tienda_a, tienda_b, dueno_a):
    respuesta = como(admin_plataforma).get("/api/plataforma/tiendas")

    assert respuesta.status_code == 200
    por_slug = {t["slug"]: t for t in respuesta.json()}
    assert set(por_slug) == {"tienda-a", "tienda-b"}
    assert por_slug["tienda-a"]["dueno"]["email"] == dueno_a.email


def test_el_admin_crea_una_tienda_con_su_dueno(admin_plataforma):
    respuesta = como(admin_plataforma).post(
        "/api/plataforma/tiendas",
        {
            "nombre": "Ferretería Sur",
            "slug": "ferreteria-sur",
            "plan": Plan.PREMIUM,
            "plantilla": "moderna",
            "duenoNombre": "Luis",
            "duenoEmail": "luis@ejemplo.cl",
            "duenoPassword": "Clave-Segura-2026",
        },
        format="json",
    )

    assert respuesta.status_code == 201
    tienda = Tienda.objects.get(slug="ferreteria-sur")
    assert tienda.plantilla == "moderna"
    dueno = Usuario.objects.get(email="luis@ejemplo.cl")
    assert dueno.rol == Rol.DUENO_TIENDA and dueno.tienda == tienda
    assert Registro.objects.filter(tienda=tienda, accion=Accion.CREAR).exists()


def test_el_admin_desactiva_una_tienda(admin_plataforma, tienda_b):
    respuesta = como(admin_plataforma).patch(
        f"/api/plataforma/tiendas/{tienda_b.slug}", {"activa": False}, format="json"
    )

    assert respuesta.status_code == 200
    tienda_b.refresh_from_db()
    assert not tienda_b.activa


def test_el_registro_anota_cambios_campo_por_campo(dueno_a, tienda_a, admin_plataforma):
    como(dueno_a).patch(
        "/api/panel/tienda", {"nombre": "Tienda Nueva"}, format="multipart"
    )

    registro = Registro.objects.filter(tienda=tienda_a, accion=Accion.MODIFICAR).first()
    assert registro is not None
    assert registro.usuario == dueno_a
    assert registro.detalle["nombre"] == {
        "antes": "Tienda A",
        "despues": "Tienda Nueva",
    }

    respuesta = como(admin_plataforma).get("/api/plataforma/registros?tienda=tienda-a")
    assert respuesta.status_code == 200
    assert respuesta.json()["count"] >= 1


def test_el_registro_nunca_guarda_contrasenas(dueno_a):
    como(dueno_a).post(
        "/api/auth/contrasena",
        {"actual": "clave-de-prueba", "nueva": "Otra-Clave-Segura-2026"},
        format="json",
    )

    for registro in Registro.objects.all():
        assert "password" not in registro.detalle
        assert "Otra-Clave" not in str(registro.detalle)
