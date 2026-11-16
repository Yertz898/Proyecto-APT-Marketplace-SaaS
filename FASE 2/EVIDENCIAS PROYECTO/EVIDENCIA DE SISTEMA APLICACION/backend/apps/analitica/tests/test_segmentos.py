"""
La segmentación de compradores.

Lo que se prueba sobre todo es **de dónde sale el umbral**. El número que
decide quién está «perdido» no se elige a mano: se calcula con los
intervalos entre compras de cada tienda. Un umbral inventado pondría en la
lista de recuperación a gente que compra cada seis meses y siempre vuelve.

Lo de acá es la línea base, no el clasificador. Cuando exista el modelo,
estas pruebas definen qué tiene que seguir cumpliendo.
"""

import pytest

from apps.analitica import segmentos
from apps.analitica.segmentos import Segmento
from apps.pedidos.models import Pedido

pytestmark = pytest.mark.django_db

SEGMENTOS = "/api/panel/segmentos"


def como(client, usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


def de(resumen, nombre):
    return next(c for c in resumen.clientes if c.nombre == nombre)


def ritmo(crear_pedido, tienda, producto, cliente, dias):
    """Un cliente que compró en cada uno de esos días hacia atrás."""
    for hace in dias:
        crear_pedido(tienda, producto, hace_dias=hace, cliente=cliente)


# ── El umbral ───────────────────────────────────────────────────────────────


def test_sin_clientes_repetidos_el_umbral_es_el_por_omision(
    tienda_a, producto_a, crear_pedido
):
    """
    Una tienda nueva no tiene patrón de recompra que romper. Se usa el plazo
    por omisión y se declara que no se midió, para que la pantalla no
    muestre un número que parece calculado.
    """
    for i in range(5):
        crear_pedido(tienda_a, producto_a, hace_dias=i, cliente=f"Cliente {i}")

    resumen = segmentos.segmentar(tienda_a)

    assert resumen.umbral == segmentos.DIAS_POR_OMISION
    assert not resumen.umbral_calculado


def test_con_suficientes_recompras_el_umbral_sale_de_los_datos(
    tienda_a, producto_a, crear_pedido
):
    """
    El percentil 90 de los intervalos: si nueve de cada diez veces alguien
    vuelve antes de ese plazo, quien lo pasó rompió su propio patrón.
    """
    # Veinticinco clientes que compran cada diez días, y uno lento.
    for i in range(25):
        ritmo(crear_pedido, tienda_a, producto_a, f"Rápido {i}", [10, 20])
    ritmo(crear_pedido, tienda_a, producto_a, "Lento", [5, 200])

    resumen = segmentos.segmentar(tienda_a)

    assert resumen.umbral_calculado
    assert 10 <= resumen.umbral <= 195


# ── Los cuatro grupos ───────────────────────────────────────────────────────


def test_quien_compro_varias_veces_y_volvio_hace_poco_es_habitual(
    tienda_a, producto_a, crear_pedido
):
    ritmo(crear_pedido, tienda_a, producto_a, "Fiel", [2, 20, 40])

    assert de(segmentos.segmentar(tienda_a), "Fiel").segmento == Segmento.HABITUAL


def test_quien_compro_una_sola_vez_y_hace_poco_es_nuevo(
    tienda_a, producto_a, crear_pedido
):
    """Todavía no es un hábito: una compra no dice si va a volver."""
    crear_pedido(tienda_a, producto_a, hace_dias=3, cliente="Recién")

    assert de(segmentos.segmentar(tienda_a), "Recién").segmento == Segmento.NUEVO


def test_quien_paso_el_umbral_esta_en_riesgo(tienda_a, producto_a, crear_pedido):
    ritmo(crear_pedido, tienda_a, producto_a, "Se enfría", [120, 200])

    cliente = de(segmentos.segmentar(tienda_a), "Se enfría")

    assert cliente.segmento == Segmento.EN_RIESGO
    # Un día de holgura a cada lado: Chile cambia la hora y ciento veinte días
    # atrás puede cruzar ese cambio; y pasada la medianoche de Chile, el pedido
    # creado «hace 120 días» en UTC cae en otro día del calendario local.
    assert 119 <= cliente.recencia <= 121


def test_quien_paso_el_doble_del_umbral_ya_se_fue(tienda_a, producto_a, crear_pedido):
    """
    «Perdido» empieza al doble y no al umbral: entre uno y otro hay alguien a
    quien todavía tiene sentido escribirle, y mezclarlo con quien se fue hace
    un año haría que el dueño no le escriba a ninguno.
    """
    ritmo(crear_pedido, tienda_a, producto_a, "Hace años", [400, 500])

    assert de(segmentos.segmentar(tienda_a), "Hace años").segmento == Segmento.PERDIDO


def test_el_resumen_cuenta_cuantos_hay_en_cada_grupo(
    tienda_a, producto_a, crear_pedido
):
    crear_pedido(tienda_a, producto_a, hace_dias=1, cliente="Nuevo")
    ritmo(crear_pedido, tienda_a, producto_a, "Habitual", [2, 15])
    ritmo(crear_pedido, tienda_a, producto_a, "Perdido", [400, 450])

    conteo = segmentos.segmentar(tienda_a).conteo

    assert conteo[Segmento.NUEVO] == 1
    assert conteo[Segmento.HABITUAL] == 1
    assert conteo[Segmento.PERDIDO] == 1
    assert conteo[Segmento.EN_RIESGO] == 0


# ── Qué cuenta como compra ──────────────────────────────────────────────────


def test_un_pedido_anulado_no_hace_cliente(tienda_a, producto_a, crear_pedido):
    crear_pedido(
        tienda_a,
        producto_a,
        hace_dias=1,
        cliente="Se arrepintió",
        estado=Pedido.Estado.CANCELADO,
    )

    assert segmentos.segmentar(tienda_a).clientes == []


def test_un_pedido_pendiente_todavia_no_hace_cliente(
    tienda_a, producto_a, crear_pedido
):
    """El pago se coordina fuera de la plataforma: puede no concretarse."""
    crear_pedido(
        tienda_a,
        producto_a,
        hace_dias=1,
        cliente="Preguntó",
        estado=Pedido.Estado.PENDIENTE,
    )

    assert segmentos.segmentar(tienda_a).clientes == []


def test_el_monto_suma_todas_sus_compras(tienda_a, producto_a, crear_pedido):
    crear_pedido(tienda_a, producto_a, hace_dias=5, neto=1000, cliente="Suma")
    crear_pedido(tienda_a, producto_a, hace_dias=10, neto=2000, cliente="Suma")

    cliente = de(segmentos.segmentar(tienda_a), "Suma")

    assert cliente.frecuencia == 2
    assert cliente.monto == 1190 + 2380


# ── Orden, aislamiento y acceso ─────────────────────────────────────────────


def test_primero_va_quien_mas_gasto_y_se_esta_yendo(tienda_a, producto_a, crear_pedido):
    """Es la lista que el dueño va a usar para escribirle a alguien."""
    ritmo(crear_pedido, tienda_a, producto_a, "Poco", [120, 200])
    crear_pedido(tienda_a, producto_a, hace_dias=130, neto=900_000, cliente="Mucho")
    crear_pedido(tienda_a, producto_a, hace_dias=250, neto=900_000, cliente="Mucho")
    crear_pedido(tienda_a, producto_a, hace_dias=1, cliente="Activo")

    primeros = [c.nombre for c in segmentos.segmentar(tienda_a).clientes[:2]]

    assert primeros == ["Mucho", "Poco"]


def test_una_tienda_no_ve_los_clientes_de_la_otra(
    tienda_a, tienda_b, producto_b, crear_pedido
):
    crear_pedido(tienda_b, producto_b, hace_dias=1, cliente="De la B")

    assert segmentos.segmentar(tienda_a).clientes == []
    assert len(segmentos.segmentar(tienda_b).clientes) == 1


def test_el_endpoint_explica_cada_segmento(
    client, tienda_a, dueno_a, producto_a, crear_pedido
):
    """
    Los nombres de los grupos no se explican solos. «En riesgo» de qué, y
    comparado con qué plazo, tiene que venir en la respuesta.
    """
    crear_pedido(tienda_a, producto_a, hace_dias=1, cliente="Alguien")

    cuerpo = como(client, dueno_a).get(SEGMENTOS).json()

    assert cuerpo["metodo"] == "regla por recencia (línea base)"
    assert cuerpo["umbralDeDias"] == segmentos.DIAS_POR_OMISION
    assert cuerpo["umbralCalculado"] is False
    assert set(cuerpo["descripciones"]) == set(segmentos.DESCRIPCION)


def test_el_endpoint_pide_sesion(client):
    assert client.get(SEGMENTOS).status_code in (401, 403)


def test_un_comprador_no_ve_los_segmentos(client, comprador):
    """Es la lista de clientes de la tienda: de lo más privado que guarda."""
    assert como(client, comprador).get(SEGMENTOS).status_code == 403
