"""La misma fixture de pedidos que usa analítica: el asistente lee de ahí."""

import pytest

from apps.analitica.tests.conftest import crear_pedido  # noqa: F401


@pytest.fixture(autouse=True)
def sin_modelo(settings):
    """
    Ninguna prueba llama a Gemini de verdad.

    Aunque el `.env` de quien corre las pruebas tenga una clave, acá se vacía:
    una prueba que depende de internet y de un plan gratuito falla por razones
    que no tienen nada que ver con el código. Las que necesitan el modelo lo
    simulan.
    """
    settings.GEMINI_API_KEY = ""
