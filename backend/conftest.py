"""
Configuración común de pytest para todo el backend.

Las fixtures base de datos (siempre dos tiendas, ver CONVENCIONES.md > Pruebas) se
agregan acá cuando existan los modelos.
"""

from decimal import Decimal

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


@pytest.fixture(autouse=True)
def _sin_intentos_acumulados():
    """
    Parte cada prueba con el contador de intentos en cero.

    El control de frecuencia de la autenticación lleva la cuenta en la caché, y
    la caché vive en memoria durante toda la corrida: sin esto, una prueba que
    inicia sesión varias veces haría fallar a la siguiente por un 429 que no
    tiene nada que ver con lo que está probando.
    """
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def detalles_de_error():
    """
    Los errores campo por campo de una respuesta.

    La API tiene un formato único de error (CONVENCIONES.md > Errores y respuestas de
    la API); esto evita repetir la ruta hasta los detalles en cada prueba.
    """

    def _detalles(respuesta):
        return respuesta.json()["error"]["detalles"]

    return _detalles


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
def dueno_b(tienda_b):
    from apps.usuarios.models import Rol, Usuario

    return Usuario.objects.create_user(
        email="dueno.b@ejemplo.cl",
        password="clave-de-prueba",
        nombre="Dueño B",
        rol=Rol.DUENO_TIENDA,
        tienda=tienda_b,
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
def configuracion_a(tienda_a):
    from apps.agenda.models import ConfiguracionAgenda

    return ConfiguracionAgenda.objects.create(
        tienda=tienda_a,
        direccion="Av. Siempre Viva 742, Ñuñoa",
        correo_notificaciones="agenda.a@ejemplo.cl",
    )


@pytest.fixture
def codigos_de_error():
    """
    Los `code` de un ValidationError, no sus mensajes.

    El texto de un mensaje se puede reescribir sin romper nada; el código es el
    contrato. Afirmar sobre el código deja las pruebas atadas a la regla y no a
    su redacción.
    """

    def _codigos(excinfo):
        error = excinfo.value
        if hasattr(error, "error_dict"):
            return {
                e.code
                for errores in error.error_dict.values()
                for e in errores
                if e.code
            }
        return {e.code for e in error.error_list if e.code}

    return _codigos


# ── Catálogo, en las dos tiendas ────────────────────────────────────────────
#
# Cada fixture tiene su gemela en la otra tienda. Esa simetría es la que
# permite probar el aislamiento en los dos sentidos: que A no ve lo de B y que
# B no ve lo de A.


@pytest.fixture
def crear_categoria(db):
    def _crear(tienda, nombre="anillos"):
        from apps.catalogo.models import Categoria

        return Categoria.objects.create(tienda=tienda, nombre=nombre)

    return _crear


@pytest.fixture
def crear_producto(db):
    """
    Un producto cualquiera, por unidad y con inventario.

    Es el caso corriente de una tienda de retail. Las otras dos formas de venta
    tienen su propia fixture porque arrastran cosas distintas: el lote, su
    composición; el peso, sus tramos.
    """

    def _crear(tienda, codigo="PROD-01", **extra):
        from apps.catalogo.models import FormaVenta, Producto, UnidadMedida

        datos = {
            "tienda": tienda,
            "codigo": codigo,
            "nombre": f"Producto {codigo} (ejemplo)",
            "precio_neto": 4990,
            "forma_venta": FormaVenta.UNIDAD,
            "unidad_medida": UnidadMedida.UNIDAD,
            "controla_stock": True,
            "stock": Decimal("25"),
        }
        datos.update(extra)
        return Producto.objects.create(**datos)

    return _crear


@pytest.fixture
def crear_lote(db):
    """Un producto vendido por lote, con su composición ya cuadrada."""

    def _crear(tienda, codigo="DEMO-01", categoria=None, piezas=10, **extra):
        from apps.catalogo.models import (
            Categoria,
            ComposicionLote,
            FormaVenta,
            Producto,
            UnidadMedida,
        )

        categoria = categoria or Categoria.objects.create(
            tienda=tienda, nombre=f"categoria-{codigo}"
        )
        datos = {
            "tienda": tienda,
            "codigo": codigo,
            "nombre": f"Lote {codigo} (ejemplo)",
            "descripcion": "Enchape de plata.",
            "precio_neto": 45990,
            "forma_venta": FormaVenta.LOTE,
            "unidad_medida": UnidadMedida.UNIDAD,
            "controla_stock": True,
            "stock": Decimal("3"),
            "cantidad_piezas": piezas,
        }
        datos.update(extra)
        producto = Producto.objects.create(**datos)
        ComposicionLote.objects.create(
            tienda=tienda, producto=producto, categoria=categoria, cantidad=piezas
        )
        return producto

    return _crear


@pytest.fixture
def crear_granel(db):
    """
    Un producto vendido por peso, sin inventario y con un tramo mínimo.

    El tramo por monto es el que fija la compra mínima: bajo ese monto de
    referencia, cotizar se rechaza.
    """

    def _crear(tienda, codigo="granel-hombre", **extra):
        from apps.catalogo.models import FormaVenta, Producto, UnidadMedida
        from apps.precios.models import TramoPrecio, UnidadUmbral

        datos = {
            "tienda": tienda,
            "codigo": codigo,
            "nombre": f"Gramo de {codigo}",
            "descripcion": "Enchape de plata.",
            "precio_neto": 650,
            "forma_venta": FormaVenta.PESO,
            "unidad_medida": UnidadMedida.GRAMO,
            "controla_stock": False,
            "stock": None,
        }
        datos.update(extra)
        producto = Producto.objects.create(**datos)
        TramoPrecio.objects.create(
            tienda=tienda,
            producto=producto,
            unidad_umbral=UnidadUmbral.MONTO,
            umbral=20000,
            valor=producto.precio_neto,
        )
        return producto

    return _crear


@pytest.fixture
def producto_a(tienda_a, crear_producto):
    return crear_producto(tienda_a, codigo="A-100")


@pytest.fixture
def producto_b(tienda_b, crear_producto):
    return crear_producto(tienda_b, codigo="B-100")


@pytest.fixture
def lote_a(tienda_a, crear_lote):
    return crear_lote(tienda_a, codigo="A-001")


@pytest.fixture
def lote_b(tienda_b, crear_lote):
    return crear_lote(tienda_b, codigo="B-001")


@pytest.fixture
def granel_a(tienda_a, crear_granel):
    return crear_granel(tienda_a, codigo="granel-a")


@pytest.fixture
def granel_b(tienda_b, crear_granel):
    return crear_granel(tienda_b, codigo="granel-b")


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
