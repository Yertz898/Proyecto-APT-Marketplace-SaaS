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


# ── Fixtures base ───────────────────────────────────────────────────────────
#
# Siempre dos tiendas con datos. Una prueba que corre con una sola tienda no
# puede detectar una fuga de aislamiento, que es el error más grave del sistema
# (CONVENCIONES.md > Pruebas).


@pytest.fixture
def tienda_a(db):
    from apps.tiendas.models import Tienda

    return Tienda.objects.create(slug="tienda-a", nombre="Tienda A")


@pytest.fixture
def tienda_b(db):
    from apps.tiendas.models import Tienda

    return Tienda.objects.create(slug="tienda-b", nombre="Tienda B")


@pytest.fixture
def dueno_a(tienda_a):
    from apps.usuarios.models import Rol, Usuario

    return Usuario.objects.create_user(
        email="dueno.a@ejemplo.cl",
        password="clave-de-prueba",
        nombre="Dueño A",
        rol=Rol.DUENO_TIENDA,
        tienda=tienda_a,
    )


@pytest.fixture
def vendedor_b(tienda_b):
    from apps.usuarios.models import Rol, Usuario

    return Usuario.objects.create_user(
        email="vendedor.b@ejemplo.cl",
        password="clave-de-prueba",
        nombre="Vendedor B",
        rol=Rol.VENDEDOR,
        tienda=tienda_b,
    )


@pytest.fixture
def comprador(db):
    from apps.usuarios.models import Rol, Usuario

    return Usuario.objects.create_user(
        email="compradora@ejemplo.cl",
        password="clave-de-prueba",
        nombre="Compradora",
        rol=Rol.COMPRADOR,
    )


@pytest.fixture
def admin_plataforma(db):
    from apps.usuarios.models import Rol, Usuario

    return Usuario.objects.create_user(
        email="plataforma@ejemplo.cl",
        password="clave-de-prueba",
        nombre="Plataforma",
        rol=Rol.ADMIN_PLATAFORMA,
    )


@pytest.fixture
def aprobacion_a(tienda_a, comprador):
    from apps.clientes.models import AprobacionMayorista, EstadoMayorista

    return AprobacionMayorista.objects.create(
        tienda=tienda_a,
        comprador=comprador,
        estado=EstadoMayorista.APROBADO,
    )


@pytest.fixture
def aprobacion_b(tienda_b, comprador):
    from apps.clientes.models import AprobacionMayorista, EstadoMayorista

    return AprobacionMayorista.objects.create(
        tienda=tienda_b,
        comprador=comprador,
        estado=EstadoMayorista.PENDIENTE,
    )
