"""
La respuesta libre: lo que no es ninguna pregunta conocida.

El modelo la redacta con la ficha de la tienda. Lo que no puede fallar: que la
ficha sea solo de la tienda de quien pregunta, que no lleve datos personales
de clientes, y que sin modelo (o con el modelo caído) quede el «no entendí».
"""

import json
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.asistente import ficha
from apps.catalogo.models import Producto

pytestmark = pytest.mark.django_db

ASISTENTE = "/api/panel/asistente"


class ClienteFalso:
    """Primero clasifica (no_entendi) y después redacta."""

    pedidos: list = []
    redaccion = "Tienes 2 productos publicados."
    error_al_redactar = None

    def __init__(self, api_key):
        self.interactions = self

    def create(self, **pedido):
        ClienteFalso.pedidos.append(pedido)
        if "schema" in str(pedido.get("response_format", "")):
            return SimpleNamespace(output_text='{"intencion": "no_entendi"}')
        if ClienteFalso.error_al_redactar:
            raise ClienteFalso.error_al_redactar
        return SimpleNamespace(output_text=ClienteFalso.redaccion)


@pytest.fixture
def con_gemini(settings, monkeypatch):
    from google import genai

    settings.GEMINI_API_KEY = "clave-de-prueba"
    ClienteFalso.pedidos = []
    ClienteFalso.redaccion = "Tienes 2 productos publicados."
    ClienteFalso.error_al_redactar = None
    monkeypatch.setattr(genai, "Client", ClienteFalso)
    return ClienteFalso


def preguntar(client, usuario, texto):
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client.post(ASISTENTE, {"pregunta": texto}, content_type="application/json")


def producto(tienda, codigo, nombre, precio):
    return Producto.objects.create(
        tienda=tienda,
        codigo=codigo,
        nombre=nombre,
        precio_neto=precio,
        forma_venta="unidad",
        unidad_medida="unidad",
        controla_stock=False,
    )


def test_una_pregunta_desconocida_la_redacta_el_modelo(client, dueno_a, con_gemini):
    cuerpo = preguntar(client, dueno_a, "cuantos productos tengo").json()

    assert cuerpo["intencion"] == "consulta_libre"
    assert cuerpo["texto"] == "Tienes 2 productos publicados."
    assert cuerpo["clasificadoPor"] == "modelo"


def test_la_ficha_es_solo_de_la_tienda_de_quien_pregunta(
    client, dueno_a, tienda_a, tienda_b, con_gemini
):
    producto(tienda_a, "A1", "Anillo de la tienda A", 1000)
    producto(tienda_b, "B1", "Collar secreto de la tienda B", 99999)

    preguntar(client, dueno_a, "cual es mi producto mas caro")

    enviado = con_gemini.pedidos[-1]["input"]
    assert "Anillo de la tienda A" in enviado
    assert "Collar secreto de la tienda B" not in enviado
    assert tienda_b.nombre not in enviado


def test_la_ficha_no_lleva_datos_personales_de_clientes(tienda_a, crear_pedido):
    anillo = producto(tienda_a, "A1", "Anillo", 1000)
    crear_pedido(tienda_a, anillo, cliente="Rosa Pérez Única")

    texto = json.dumps(ficha.armar(tienda_a), ensure_ascii=False, default=str)

    assert "Anillo" in texto
    assert "Rosa Pérez Única" not in texto
    assert "+56900000000" not in texto


def test_sin_modelo_queda_el_no_entendi(client, dueno_a):
    cuerpo = preguntar(client, dueno_a, "cuantos productos tengo").json()

    assert cuerpo["intencion"] == "no_entendi"


def test_si_el_modelo_falla_al_redactar_queda_el_no_entendi(
    client, dueno_a, con_gemini
):
    con_gemini.error_al_redactar = TimeoutError("se demoró")

    cuerpo = preguntar(client, dueno_a, "cuantos productos tengo").json()

    assert cuerpo["intencion"] == "no_entendi"


def test_una_pregunta_conocida_no_pasa_por_la_redaccion(
    client, dueno_a, settings, monkeypatch
):
    from google import genai

    class SoloClasifica(ClienteFalso):
        def create(self, **pedido):
            formato = str(pedido.get("response_format", ""))
            assert "schema" in formato, "no debía redactar"
            return SimpleNamespace(output_text='{"intencion": "ventas_del_mes"}')

    settings.GEMINI_API_KEY = "clave-de-prueba"
    monkeypatch.setattr(genai, "Client", SoloClasifica)

    cuerpo = preguntar(client, dueno_a, "como van mis ventas").json()

    assert cuerpo["intencion"] == "ventas_del_mes"


# ── Fechas y rangos: los resuelve el backend, no el modelo ──────────────────

HOY = date(2026, 11, 16)


@pytest.mark.parametrize(
    ("pregunta", "esperadas"),
    [
        ("cuanto vendi el 15 de diciembre de 2025", [date(2025, 12, 15)]),
        # Sin año: el último 3 de octubre, aunque ese día no haya ventas.
        ("que vendi el 3 de octubre", [date(2026, 10, 3)]),
        # Sin año y todavía no llega este año: el del año pasado.
        ("y el 24 de diciembre", [date(2025, 12, 24)]),
        ("cuanto vendi el 28 12 2025", [date(2025, 12, 28)]),
        ("cuanto vendi ayer", [date(2026, 11, 15)]),
        ("cuanto vendi el 31 de febrero", []),
        ("cuantos productos tengo", []),
    ],
)
def test_entiende_las_fechas_de_la_pregunta(pregunta, esperadas):
    assert ficha.fechas_de_la_pregunta(pregunta, HOY) == esperadas


@pytest.mark.parametrize(
    ("pregunta", "esperado"),
    [
        (
            "cuanto vendi entre el 1 y el 10 de diciembre de 2025",
            [(date(2025, 12, 1), date(2025, 12, 10))],
        ),
        (
            "del 20 de noviembre al 5 de diciembre de 2025",
            [(date(2025, 11, 20), date(2025, 12, 5))],
        ),
        ("del 1 al 5 de octubre", [(date(2026, 10, 1), date(2026, 10, 5))]),
    ],
)
def test_entiende_los_rangos_de_la_pregunta(pregunta, esperado):
    assert ficha.rangos_de_la_pregunta(pregunta, HOY) == esperado


def test_la_ficha_trae_el_dia_y_el_rango_ya_sumados(tienda_a, crear_pedido):
    anillo = producto(tienda_a, "A1", "Anillo", 1000)
    crear_pedido(tienda_a, anillo, neto=1000, hace_dias=1)
    crear_pedido(tienda_a, anillo, neto=2000, hace_dias=1)
    ayer = date.today() - timedelta(days=1)
    pregunta = f"cuanto vendi el {ayer.day} {ayer.month} {ayer.year}"

    datos = ficha.armar(tienda_a, pregunta=pregunta)

    (dia,) = datos["diasQueNombraLaPregunta"]
    assert dia["fecha"] == ayer.isoformat()
    assert dia["pedidos"] == 2
    assert dia["total"] == 1190 + 2380
    assert dia["ticketPromedio"] == round((1190 + 2380) / 2)
