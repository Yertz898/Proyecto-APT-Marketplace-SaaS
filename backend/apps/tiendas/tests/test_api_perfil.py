"""
Perfil de la tienda en el panel: GET y PATCH de /api/panel/tienda.

La tienda sale del token, así que no hay identificador que forzar. Las pruebas
de aislamiento lo comprueban del único modo que queda: dos tiendas con perfiles
distintos, y cada dueño viendo y tocando el suyo.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.tiendas.models import Plan, Tipografia

pytestmark = pytest.mark.django_db

PERFIL = "/api/panel/tienda"


def como(client, usuario):
    """Cliente autenticado con el token de ese usuario."""
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


def editar(client, **datos):
    return client.patch(PERFIL, datos, content_type="application/json")


def subir(client, **archivos):
    """
    PATCH con archivos.

    El cliente de Django arma el multipart solo en `post`; en `patch` hay que
    entregarle el cuerpo ya codificado.
    """
    from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart

    return client.patch(
        PERFIL, encode_multipart(BOUNDARY, archivos), content_type=MULTIPART_CONTENT
    )


def imagen(nombre="logo.png"):
    """Una imagen de verdad, hecha en memoria."""
    memoria = io.BytesIO()
    Image.new("RGB", (8, 8), "#1f4e79").save(memoria, format="PNG")
    return SimpleUploadedFile(nombre, memoria.getvalue(), content_type="image/png")


@pytest.fixture
def premium_a(tienda_a):
    tienda_a.plan = Plan.PREMIUM
    tienda_a.save(update_fields=["plan"])
    return tienda_a


# ── Leer el perfil ──────────────────────────────────────────────────────────


def test_el_dueno_ve_el_perfil_de_su_tienda(client, dueno_a, tienda_a, tienda_b):
    cuerpo = como(client, dueno_a).get(PERFIL).json()

    assert cuerpo["slug"] == tienda_a.slug
    assert cuerpo["nombre"] == tienda_a.nombre
    assert cuerpo["plan"] == tienda_a.plan


def test_el_perfil_trae_las_tipografias_que_se_pueden_elegir(client, dueno_a):
    disponibles = como(client, dueno_a).get(PERFIL).json()["tipografiasDisponibles"]

    assert [t["valor"] for t in disponibles] == [v for v, _ in Tipografia.choices]


def test_el_perfil_dice_si_el_plan_deja_editar_la_marca(client, dueno_a, premium_a):
    assert como(client, dueno_a).get(PERFIL).json()["puedeEditarLaMarca"] is True


def test_en_el_plan_basico_la_marca_no_se_puede_editar(client, dueno_a, tienda_a):
    assert tienda_a.plan == Plan.BASICO
    assert como(client, dueno_a).get(PERFIL).json()["puedeEditarLaMarca"] is False


def test_sin_sesion_no_hay_perfil(client, tienda_a):
    assert client.get(PERFIL).status_code == 401


def test_un_comprador_no_tiene_perfil_de_tienda(client, comprador):
    assert como(client, comprador).get(PERFIL).status_code == 403


# ── Editar el perfil ────────────────────────────────────────────────────────


def test_el_dueno_cambia_el_nombre_de_su_tienda(client, dueno_a, tienda_a):
    respuesta = editar(como(client, dueno_a), nombre="Joyas de Prueba")

    assert respuesta.status_code == 200
    tienda_a.refresh_from_db()
    assert tienda_a.nombre == "Joyas de Prueba"


def test_el_dueno_cambia_los_colores(client, dueno_a, premium_a):
    respuesta = editar(
        como(client, dueno_a),
        colorPrimario="#7C3AED",
        colorPrimarioHover="#6D28D9",
        colorAcento="#F59E0B",
        colorDestacado="#10B981",
    )

    assert respuesta.status_code == 200
    premium_a.refresh_from_db()
    assert premium_a.color_primario == "#7C3AED"
    assert premium_a.color_destacado == "#10B981"


def test_el_dueno_elige_una_tipografia_de_la_lista(client, dueno_a, premium_a):
    assert editar(como(client, dueno_a), tipografia="manrope").status_code == 200
    premium_a.refresh_from_db()
    assert premium_a.tipografia == "manrope"


def test_una_tipografia_fuera_de_la_lista_se_rechaza(
    client, dueno_a, premium_a, detalles_de_error
):
    respuesta = editar(como(client, dueno_a), tipografia="Comic Sans")

    assert respuesta.status_code == 400
    assert "tipografia" in detalles_de_error(respuesta)


def test_el_slug_no_se_puede_cambiar(client, dueno_a, tienda_a):
    editar(como(client, dueno_a), slug="otro-slug")

    tienda_a.refresh_from_db()
    assert tienda_a.slug == "tienda-a"


def test_el_plan_no_se_puede_cambiar_desde_la_tienda(client, dueno_a, tienda_a):
    editar(como(client, dueno_a), plan=Plan.ULTIMATE)

    tienda_a.refresh_from_db()
    assert tienda_a.plan == Plan.BASICO


# ── Colores: el validador que evita CSS ajeno ───────────────────────────────


@pytest.mark.parametrize(
    "color",
    [
        "rojo",
        "#ABC",
        "#12345",
        "#1234567",
        "red; background: url(http://malo)",
        "var(--color-marino)",
    ],
)
def test_un_color_que_no_es_hexadecimal_se_rechaza(
    client, dueno_a, premium_a, detalles_de_error, color
):
    respuesta = editar(como(client, dueno_a), colorPrimario=color)

    assert respuesta.status_code == 400
    assert "colorPrimario" in detalles_de_error(respuesta)


def test_un_color_invalido_no_deja_a_medias_los_demas(client, dueno_a, premium_a):
    editar(como(client, dueno_a), colorPrimario="#7C3AED", colorAcento="azul")

    premium_a.refresh_from_db()
    assert premium_a.color_primario == ""


# ── Imágenes: por contenido, no por el nombre del archivo ───────────────────


def test_el_dueno_sube_el_logo(client, dueno_a, tienda_a):
    respuesta = subir(como(client, dueno_a), logo=imagen())

    assert respuesta.status_code == 200
    assert respuesta.json()["logoActual"]["url"]
    tienda_a.refresh_from_db()
    assert tienda_a.logo


def test_un_archivo_que_no_es_imagen_se_rechaza(
    client, dueno_a, tienda_a, detalles_de_error
):
    disfrazado = SimpleUploadedFile(
        "logo.png", b"<svg onload=alert(1)></svg>", content_type="image/png"
    )
    respuesta = subir(como(client, dueno_a), logo=disfrazado)

    assert respuesta.status_code == 400
    assert "logo" in detalles_de_error(respuesta)
    tienda_a.refresh_from_db()
    assert not tienda_a.logo


# ── El plan decide, no la interfaz ──────────────────────────────────────────


def test_en_el_plan_basico_el_logo_si_se_puede(client, dueno_a, tienda_a):
    assert subir(como(client, dueno_a), logo=imagen()).status_code == 200


def test_en_el_plan_basico_el_resto_de_la_marca_se_rechaza(
    client, dueno_a, tienda_a, detalles_de_error
):
    respuesta = editar(como(client, dueno_a), colorPrimario="#7C3AED")

    assert respuesta.status_code == 400
    assert "color_primario" in detalles_de_error(respuesta)
    tienda_a.refresh_from_db()
    assert tienda_a.color_primario == ""


def test_el_plan_premium_abre_la_marca(client, dueno_a, premium_a):
    respuesta = editar(como(client, dueno_a), instagram="https://instagram.com/joyas")

    assert respuesta.status_code == 200


# ── Roles ───────────────────────────────────────────────────────────────────


def test_el_vendedor_ve_el_perfil_de_su_tienda(client, vendedor_b, tienda_b):
    respuesta = como(client, vendedor_b).get(PERFIL)

    assert respuesta.status_code == 200
    assert respuesta.json()["slug"] == tienda_b.slug


def test_el_vendedor_no_puede_editar_el_perfil(client, vendedor_b, tienda_b):
    respuesta = editar(como(client, vendedor_b), nombre="Nombre del vendedor")

    assert respuesta.status_code == 403
    tienda_b.refresh_from_db()
    assert tienda_b.nombre == "Tienda B"


def test_un_comprador_no_puede_editar_ningun_perfil(client, comprador, tienda_a):
    assert editar(como(client, comprador), nombre="Mía").status_code == 403


# ── Aislamiento ─────────────────────────────────────────────────────────────


@pytest.mark.aislamiento
def test_cada_dueno_ve_solo_el_perfil_de_su_tienda(
    client, dueno_a, dueno_b, tienda_a, tienda_b
):
    de_a = como(client, dueno_a).get(PERFIL).json()
    de_b = como(client, dueno_b).get(PERFIL).json()

    assert de_a["slug"] == tienda_a.slug
    assert de_b["slug"] == tienda_b.slug


@pytest.mark.aislamiento
def test_el_dueno_de_a_no_toca_la_tienda_b(client, dueno_a, tienda_a, tienda_b):
    editar(como(client, dueno_a), nombre="Nombre nuevo de A")

    tienda_a.refresh_from_db()
    tienda_b.refresh_from_db()
    assert tienda_a.nombre == "Nombre nuevo de A"
    assert tienda_b.nombre == "Tienda B"


@pytest.mark.aislamiento
def test_el_dueno_de_b_no_toca_la_tienda_a(client, dueno_b, tienda_a, tienda_b):
    editar(como(client, dueno_b), nombre="Nombre nuevo de B")

    tienda_a.refresh_from_db()
    tienda_b.refresh_from_db()
    assert tienda_b.nombre == "Nombre nuevo de B"
    assert tienda_a.nombre == "Tienda A"


@pytest.mark.aislamiento
def test_el_logo_que_sube_a_no_aparece_en_b(client, dueno_a, tienda_a, tienda_b):
    subir(como(client, dueno_a), logo=imagen())

    tienda_a.refresh_from_db()
    tienda_b.refresh_from_db()
    assert tienda_a.logo
    assert not tienda_b.logo


@pytest.mark.aislamiento
def test_la_vitrina_publica_refleja_el_cambio_solo_en_su_tienda(
    client, dueno_a, premium_a, tienda_b
):
    editar(como(client, dueno_a), nombre="Marca de A")
    del client.defaults["HTTP_AUTHORIZATION"]

    publica_a = client.get(f"/api/t/{premium_a.slug}/tienda").json()
    publica_b = client.get(f"/api/t/{tienda_b.slug}/tienda").json()

    assert publica_a["nombre"] == "Marca de A"
    assert publica_b["nombre"] == "Tienda B"
