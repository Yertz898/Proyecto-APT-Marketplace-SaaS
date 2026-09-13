"""
Configuración común de pytest para todo el backend.

Las fixtures base de datos (siempre dos tiendas, ver CONVENCIONES.md > Pruebas) se
agregan acá cuando existan los modelos.
"""

import pytest


@pytest.fixture(autouse=True)
def _sin_redireccion_https(settings):
    """
    Desactiva la redirección a HTTPS durante las pruebas.

    Con DEBUG=False (como corre el CI) settings.py activa SECURE_SSL_REDIRECT, y el
    cliente de pruebas hace peticiones por http: toda respuesta sería un 301 y una
    prueba de aislamiento que espera 404 fallaría por la razón equivocada.

    Se apaga solo acá, no con una variable de entorno, para que en producción no
    exista una forma de desactivarla por configuración.
    """
    settings.SECURE_SSL_REDIRECT = False
