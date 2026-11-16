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


# ── Tienda desde una solicitud ──────────────────────────────────────────────


def test_crear_la_tienda_desde_una_solicitud_la_marca_activada(admin_plataforma):
    from apps.tiendas.models import EstadoSolicitud, SolicitudDeAcceso

    solicitud = SolicitudDeAcceso.objects.create(
        negocio="Bazar Sur", nombre="Rosa", email="rosa@ejemplo.cl", telefono="+569"
    )

    respuesta = como(admin_plataforma).post(
        "/api/plataforma/tiendas",
        {
            "nombre": "Bazar Sur",
            "slug": "bazar-sur",
            "duenoNombre": "Rosa",
            "duenoEmail": "rosa@ejemplo.cl",
            "duenoPassword": "Clave-Segura-2026",
            "solicitud": solicitud.pk,
        },
        format="json",
    )

    assert respuesta.status_code == 201
    solicitud.refresh_from_db()
    assert solicitud.estado == EstadoSolicitud.ACTIVADA


# ── Tienda cerrada por la administración ────────────────────────────────────


def _cerrar(tienda):
    tienda.activa = False
    tienda.save()


def test_el_equipo_de_una_tienda_cerrada_no_inicia_sesion(client, dueno_a, tienda_a):
    _cerrar(tienda_a)

    respuesta = client.post(
        "/api/auth/sesion",
        {"email": dueno_a.email, "password": "clave-de-prueba"},
        content_type="application/json",
    )

    assert respuesta.status_code == 403
    assert "cerrada" in respuesta.json()["error"]["mensaje"]


def test_un_token_vigente_deja_de_servir_al_cerrar_la_tienda(dueno_a, tienda_a):
    cliente = como(dueno_a)
    assert cliente.get("/api/panel/tienda").status_code == 200

    _cerrar(tienda_a)

    assert cliente.get("/api/panel/tienda").status_code == 403
    assert cliente.get("/api/panel/productos").status_code == 403


def test_quien_cancelo_su_plan_si_entra_para_reanudarlo(client, dueno_a, tienda_a):
    como(dueno_a).post("/api/panel/plan/cancelar")

    respuesta = client.post(
        "/api/auth/sesion",
        {"email": dueno_a.email, "password": "clave-de-prueba"},
        content_type="application/json",
    )

    assert respuesta.status_code == 200
    assert como(dueno_a).post("/api/panel/plan/reanudar").status_code == 200


def test_reabrir_la_tienda_devuelve_el_acceso(admin_plataforma, dueno_a, tienda_a):
    _cerrar(tienda_a)
    como(admin_plataforma).patch(
        f"/api/plataforma/tiendas/{tienda_a.slug}", {"activa": True}, format="json"
    )

    assert como(dueno_a).get("/api/panel/tienda").status_code == 200


# ── Mensajes de una tienda cerrada ──────────────────────────────────────────

URL_MENSAJE = "/api/auth/mensaje-a-la-plataforma"


def _escribir(client, email, password="clave-de-prueba", mensaje="Quiero reabrir"):
    return client.post(
        URL_MENSAJE,
        {"email": email, "password": password, "mensaje": mensaje},
        content_type="application/json",
    )


def test_el_inicio_de_sesion_avisa_con_codigo_propio(client, dueno_a, tienda_a):
    _cerrar(tienda_a)

    respuesta = client.post(
        "/api/auth/sesion",
        {"email": dueno_a.email, "password": "clave-de-prueba"},
        content_type="application/json",
    )

    assert respuesta.json()["error"]["codigo"] == "tienda_cerrada"


def test_el_equipo_de_una_tienda_cerrada_escribe_y_el_admin_lo_lee(
    client, dueno_a, tienda_a, admin_plataforma
):
    _cerrar(tienda_a)

    assert _escribir(client, dueno_a.email).status_code == 201

    respuesta = como(admin_plataforma).get("/api/plataforma/mensajes")
    assert respuesta.status_code == 200
    [mensaje] = respuesta.json()
    assert mensaje["tiendaSlug"] == tienda_a.slug
    assert mensaje["mensaje"] == "Quiero reabrir"
    assert mensaje["leido"] is False

    marcado = como(admin_plataforma).patch(
        f"/api/plataforma/mensajes/{mensaje['id']}", {"leido": True}, format="json"
    )
    assert marcado.json()["leido"] is True


def test_sin_la_contrasena_correcta_no_se_escribe(client, dueno_a, tienda_a):
    from apps.tiendas.models import MensajeDeTienda

    _cerrar(tienda_a)

    respuesta = _escribir(client, dueno_a.email, password="otra")

    # Sin autenticadores en la vista, DRF responde 403 y no 401; lo que importa
    # es que no pasa y que el código dice por qué.
    assert respuesta.status_code in (401, 403)
    assert respuesta.json()["error"]["codigo"] == "credenciales_invalidas"
    assert not MensajeDeTienda.objects.exists()


def test_una_tienda_abierta_no_escribe_por_aca(client, dueno_a):
    assert _escribir(client, dueno_a.email).status_code == 400


def test_solo_el_admin_lee_los_mensajes(dueno_b):
    assert como(dueno_b).get("/api/plataforma/mensajes").status_code == 403
