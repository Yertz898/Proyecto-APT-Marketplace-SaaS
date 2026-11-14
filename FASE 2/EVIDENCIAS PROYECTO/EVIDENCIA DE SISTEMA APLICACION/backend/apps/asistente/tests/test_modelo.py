"""
El modelo de lenguaje que clasifica la pregunta.

Ninguna prueba llama a Gemini: el cliente se reemplaza por uno falso que
anota qué se le pidió y devuelve lo que la prueba decida. Lo que se prueba es
lo que no puede fallar aunque Google cambie algo: que solo viaje la pregunta,
que la respuesta del modelo nunca se use sin validar, y que cualquier falla
caiga a las palabras clave sin que el vendedor lo note.
"""

import json
from io import StringIO
from types import SimpleNamespace

import pytest
from django.core.management import call_command

from apps.asistente import clasificador, modelo
from apps.asistente.management.commands.evaluar_asistente import cargar_preguntas


class ClienteFalso:
    """Hace las veces de `genai.Client` y guarda lo que recibió."""

    pedido = None
    respuesta = '{"intencion": "pronostico"}'
    error = None

    def __init__(self, api_key):
        ClienteFalso.clave = api_key
        self.interactions = self

    def create(self, **pedido):
        ClienteFalso.pedido = pedido
        if ClienteFalso.error:
            raise ClienteFalso.error
        return SimpleNamespace(output_text=ClienteFalso.respuesta)


@pytest.fixture
def con_gemini(settings, monkeypatch):
    """Una clave configurada y el cliente de Google reemplazado por el falso."""
    from google import genai

    settings.GEMINI_API_KEY = "clave-de-prueba"
    ClienteFalso.pedido = None
    ClienteFalso.respuesta = '{"intencion": "pronostico"}'
    ClienteFalso.error = None
    monkeypatch.setattr(genai, "Client", ClienteFalso)
    return ClienteFalso


# ── Sin clave, nada cambia ──────────────────────────────────────────────────


def test_sin_clave_no_se_llama_al_modelo_y_responden_las_palabras_clave(monkeypatch):
    from google import genai

    def no_llamar(**_):
        raise AssertionError("no debía llamar a Gemini")

    monkeypatch.setattr(genai, "Client", no_llamar)

    assert clasificador.clasificar_con_origen("¿cómo van mis ventas?") == (
        "ventas_del_mes",
        clasificador.POR_PALABRAS_CLAVE,
    )


# ── Con clave ───────────────────────────────────────────────────────────────


def test_con_clave_decide_el_modelo(con_gemini):
    etiqueta, origen = clasificador.clasificar_con_origen("como se viene diciembre")

    assert (etiqueta, origen) == ("pronostico", clasificador.POR_MODELO)


def test_al_modelo_solo_le_llega_la_pregunta_limpia(con_gemini):
    """
    En el plan gratuito Google usa lo que recibe. Lo único que viaja es la
    pregunta, recortada y sin signos, y se pide que no la guarde.
    """
    clasificador.clasificar("¿Cómo se viene DICIEMBRE?!  <script>")

    pedido = con_gemini.pedido
    assert pedido["input"] == "como se viene diciembre script"
    assert pedido["store"] is False
    assert pedido["timeout"] == modelo.TIEMPO_MAXIMO


def test_la_respuesta_esta_restringida_a_la_lista_cerrada(con_gemini):
    clasificador.clasificar("como se viene diciembre")

    esquema = con_gemini.pedido["response_format"]["schema"]
    permitidas = esquema["properties"]["intencion"]["enum"]
    assert set(permitidas) == set(clasificador.RESPUESTAS)


def test_una_etiqueta_inventada_no_se_usa(con_gemini):
    """
    Aunque el esquema ya la restringe, la respuesta pasa por `_es_valida`. Si
    llegara algo fuera de la lista —por un cambio del lado de Google o una
    inyección que lograra torcerla—, mandan las palabras clave.
    """
    con_gemini.respuesta = json.dumps({"intencion": "borrar_todo"})

    etiqueta, origen = clasificador.clasificar_con_origen("cómo van mis ventas")

    assert (etiqueta, origen) == ("ventas_del_mes", clasificador.POR_PALABRAS_CLAVE)


@pytest.mark.parametrize("respuesta", ["no es json", "", "{}", '{"intencion": 7}'])
def test_una_respuesta_que_no_se_entiende_cae_a_palabras_clave(con_gemini, respuesta):
    con_gemini.respuesta = respuesta

    etiqueta, origen = clasificador.clasificar_con_origen("cómo van mis ventas")

    assert (etiqueta, origen) == ("ventas_del_mes", clasificador.POR_PALABRAS_CLAVE)


def test_si_el_modelo_falla_el_vendedor_recibe_respuesta_igual(con_gemini, caplog):
    """Sin internet, con demora o con el límite gratuito alcanzado: lo mismo."""
    con_gemini.error = TimeoutError("se demoró")

    etiqueta, origen = clasificador.clasificar_con_origen("cuánto llevo vendido")

    assert (etiqueta, origen) == ("ventas_del_mes", clasificador.POR_PALABRAS_CLAVE)
    assert "TimeoutError" in caplog.text
    assert "vendido" not in caplog.text  # la pregunta no queda en el log


def test_una_pregunta_vacia_ni_siquiera_llega_al_modelo(con_gemini):
    assert clasificador.clasificar_con_origen("¿¡ !?")[0] == "no_entendi"
    assert con_gemini.pedido is None


@pytest.mark.django_db
def test_el_endpoint_dice_quien_entendio_la_pregunta(client, dueno_a, con_gemini):
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(dueno_a)}"

    cuerpo = client.post(
        "/api/panel/asistente", {"pregunta": "como se viene diciembre"}, format="json"
    ).json()

    assert cuerpo["intencion"] == "pronostico"
    assert cuerpo["clasificadoPor"] == "modelo"


# ── El set de preguntas ─────────────────────────────────────────────────────


def test_el_set_de_preguntas_solo_usa_intenciones_que_existen():
    preguntas = cargar_preguntas()

    assert len(preguntas) >= 60
    assert {p["intencion"] for p in preguntas} == set(clasificador.RESPUESTAS)


def test_las_palabras_clave_no_retroceden_sobre_el_set():
    """
    El piso medido el 12-11-2026: 34 de 64. Si un cambio en la tabla de
    palabras lo baja, el asistente entiende menos que antes.
    """
    preguntas = cargar_preguntas()
    aciertos = sum(
        clasificador.por_palabras_clave(p["pregunta"]) == p["intencion"]
        for p in preguntas
    )

    assert aciertos >= 34


def test_sin_clave_el_comando_mide_solo_palabras_clave():
    salida = StringIO()

    call_command("evaluar_asistente", stdout=salida)

    assert "Palabras clave" in salida.getvalue()
    assert "Sin GEMINI_API_KEY" in salida.getvalue()
