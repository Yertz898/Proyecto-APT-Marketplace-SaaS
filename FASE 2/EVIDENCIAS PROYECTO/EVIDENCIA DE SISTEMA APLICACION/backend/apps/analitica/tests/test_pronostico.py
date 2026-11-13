"""
El pronóstico de demanda y la alerta de quiebre.

Lo que más se prueba es **cuándo el sistema se niega a proyectar**. Un
pronóstico equivocado no se ve equivocado: sale un número, se muestra en la
pantalla y el dueño compra mercadería con él. Por eso las negativas tienen
más pruebas que los aciertos.

Lo de acá es la línea base, no el modelo. Cuando exista el modelo, estas
mismas pruebas definen qué tiene que seguir cumpliendo.
"""

from decimal import Decimal

import pytest

from apps.analitica import pronostico
from apps.pedidos.models import Pedido

pytestmark = pytest.mark.django_db

PRONOSTICO = "/api/panel/pronostico"


def como(client, usuario):
    from rest_framework_simplejwt.tokens import AccessToken

    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(usuario)}"
    return client


def de(proyecciones, codigo):
    return next(p for p in proyecciones if p.codigo == codigo)


def con_historia(tienda, producto, venta_hace_meses, meses, cantidad=10):
    """Una venta por mes, hacia atrás, para armarle una serie al producto."""
    for mes in range(1, meses + 1):
        venta_hace_meses(tienda, producto, mes, cantidad=cantidad)


# ── Cuándo se niega a proyectar ─────────────────────────────────────────────


def test_un_producto_sin_ventas_no_se_proyecta(tienda_a, producto_a):
    proyeccion = de(pronostico.proyectar(tienda_a), producto_a.codigo)

    assert not proyeccion.suficiente
    assert proyeccion.esperado is None
    assert proyeccion.meses_con_ventas == 0


def test_un_producto_con_poca_historia_no_se_proyecta(
    tienda_a, producto_a, venta_hace_meses
):
    """
    Tres meses no son una serie de tiempo, son tres números.

    Proyectar igual sería repetir el último mes y llamarlo pronóstico.
    """
    con_historia(tienda_a, producto_a, venta_hace_meses, meses=3)

    proyeccion = de(pronostico.proyectar(tienda_a), producto_a.codigo)

    assert not proyeccion.suficiente
    assert proyeccion.meses_con_ventas == 3
    assert proyeccion.esperado is None


def test_con_el_minimo_de_meses_si_se_proyecta(tienda_a, producto_a, venta_hace_meses):
    con_historia(
        tienda_a, producto_a, venta_hace_meses, meses=pronostico.MINIMO_DE_MESES
    )

    proyeccion = de(pronostico.proyectar(tienda_a), producto_a.codigo)

    assert proyeccion.suficiente
    assert proyeccion.esperado == Decimal("10.00")


# ── Cómo se calcula ─────────────────────────────────────────────────────────


def test_el_promedio_movil_mira_solo_los_ultimos_meses():
    """Un mes viejo no puede arrastrar la proyección del próximo."""
    cantidades = [Decimal(n) for n in (1000, 1000, 1000, 10, 20, 30)]

    assert pronostico.promedio_movil(cantidades) == Decimal("20.00")


def test_la_proyeccion_sale_de_holt_y_no_del_promedio_movil(
    tienda_a, producto_a, venta_hace_meses
):
    """
    Holt le ganó al promedio móvil en la evaluación, así que es el que se
    muestra. Con ventas que caen los dos dan distinto: el promedio repite el
    nivel de los últimos tres meses y Holt sigue la caída, amortiguada.
    """
    ventas = (60, 50, 40, 30, 20, 10)
    for meses_atras, cantidad in zip(range(6, 0, -1), ventas, strict=True):
        venta_hace_meses(tienda_a, producto_a, meses_atras, cantidad=cantidad)

    proyeccion = de(pronostico.proyectar(tienda_a), producto_a.codigo)

    esperado = pronostico.holt_amortiguado(
        [60, 50, 40, 30, 20, 10], pronostico.ALFA, pronostico.BETA, pronostico.PHI
    )
    assert proyeccion.esperado == Decimal(str(esperado)).quantize(Decimal("0.01"))
    assert proyeccion.esperado < Decimal("20.00")  # el promedio móvil diría 20
    assert proyeccion.metodo == "suavizado de Holt amortiguado"


def test_el_mes_en_curso_no_entra_en_el_promedio(
    tienda_a, producto_a, venta_hace_meses, crear_pedido
):
    """
    Va por la mitad, así que siempre suma menos que un mes cerrado.

    Si entrara, la proyección bajaría cada vez que alguien abre la pantalla
    a principio de mes y subiría sola hacia fin de mes.
    """
    con_historia(tienda_a, producto_a, venta_hace_meses, meses=6, cantidad=10)
    crear_pedido(tienda_a, producto_a, cantidad=999, hace_dias=0)

    proyeccion = de(pronostico.proyectar(tienda_a), producto_a.codigo)

    assert proyeccion.esperado == Decimal("10.00")


def test_los_pedidos_anulados_no_entran_en_la_serie(
    tienda_a, producto_a, venta_hace_meses
):
    con_historia(tienda_a, producto_a, venta_hace_meses, meses=6, cantidad=10)
    for mes in range(1, 7):
        venta_hace_meses(
            tienda_a, producto_a, mes, cantidad=500, estado=Pedido.Estado.CANCELADO
        )

    proyeccion = de(pronostico.proyectar(tienda_a), producto_a.codigo)

    assert proyeccion.esperado == Decimal("10.00")


def test_un_pedido_pendiente_todavia_no_es_demanda(
    tienda_a, producto_a, venta_hace_meses
):
    con_historia(tienda_a, producto_a, venta_hace_meses, meses=6, cantidad=10)
    for mes in range(1, 7):
        venta_hace_meses(
            tienda_a, producto_a, mes, cantidad=500, estado=Pedido.Estado.PENDIENTE
        )

    assert de(pronostico.proyectar(tienda_a), producto_a.codigo).esperado == Decimal(
        "10.00"
    )


# ── La alerta de quiebre ────────────────────────────────────────────────────


def test_avisa_en_cuantos_dias_se_acaba_el_stock(
    tienda_a, crear_producto, venta_hace_meses
):
    producto = crear_producto(tienda_a, codigo="A-1", stock=Decimal("60"))
    con_historia(tienda_a, producto, venta_hace_meses, meses=6, cantidad=30)

    proyeccion = de(pronostico.proyectar(tienda_a), "A-1")

    # 30 al mes es uno al día, y quedan 60.
    assert proyeccion.dias_hasta_quiebre == 60


def test_quien_no_lleva_inventario_no_tiene_quiebre_que_anunciar(
    tienda_a, crear_granel, venta_hace_meses
):
    """
    La tienda no registra cuánto le queda del granel. Un número inventado en
    una alerta de stock es peor que no tener alerta.
    """
    granel = crear_granel(tienda_a)
    con_historia(tienda_a, granel, venta_hace_meses, meses=6, cantidad=100)

    proyeccion = de(pronostico.proyectar(tienda_a), granel.codigo)

    assert proyeccion.suficiente
    assert proyeccion.dias_hasta_quiebre is None


def test_sin_pronostico_no_hay_alerta_de_quiebre(tienda_a, crear_producto):
    """Sin saber cuánto se vende, no se puede decir cuándo se acaba."""
    crear_producto(tienda_a, codigo="A-1", stock=Decimal("5"))

    assert de(pronostico.proyectar(tienda_a), "A-1").dias_hasta_quiebre is None


def test_lo_que_se_queda_sin_stock_antes_va_primero(
    tienda_a, crear_producto, venta_hace_meses
):
    """El dueño abre esta pantalla para saber qué reponer, no para leerla entera."""
    urgente = crear_producto(tienda_a, codigo="URGENTE", stock=Decimal("30"))
    tranquilo = crear_producto(tienda_a, codigo="TRANQUILO", stock=Decimal("900"))
    con_historia(tienda_a, urgente, venta_hace_meses, meses=6, cantidad=30)
    con_historia(tienda_a, tranquilo, venta_hace_meses, meses=6, cantidad=30)

    codigos = [p.codigo for p in pronostico.proyectar(tienda_a)]

    assert codigos.index("URGENTE") < codigos.index("TRANQUILO")


# ── Aislamiento y acceso ────────────────────────────────────────────────────


def test_el_pronostico_no_mira_las_ventas_de_otra_tienda(
    tienda_a, tienda_b, crear_producto, venta_hace_meses
):
    mio = crear_producto(tienda_a, codigo="MISMO")
    ajeno = crear_producto(tienda_b, codigo="MISMO")
    con_historia(tienda_b, ajeno, venta_hace_meses, meses=12, cantidad=50)

    assert not de(pronostico.proyectar(tienda_a), mio.codigo).suficiente
    assert de(pronostico.proyectar(tienda_b), ajeno.codigo).suficiente


def test_un_producto_desactivado_no_se_proyecta(tienda_a, crear_producto):
    """Está fuera de la vitrina: no hay nada que reponer."""
    crear_producto(tienda_a, codigo="APAGADO", activo=False)

    assert not any(p.codigo == "APAGADO" for p in pronostico.proyectar(tienda_a))


def test_el_endpoint_dice_con_que_metodo_calculo(
    client, tienda_a, dueno_a, producto_a, venta_hace_meses
):
    """
    La pantalla tiene que poder decir si lo que muestra es la línea base o un
    modelo. Mientras no se distinga, nadie sabe cuánto confiar en el número.
    """
    con_historia(tienda_a, producto_a, venta_hace_meses, meses=6)

    cuerpo = como(client, dueno_a).get(PRONOSTICO).json()

    fila = next(p for p in cuerpo["productos"] if p["codigo"] == producto_a.codigo)
    assert fila["metodo"] == "suavizado de Holt amortiguado"
    assert cuerpo["minimoDeMeses"] == pronostico.MINIMO_DE_MESES


def test_el_endpoint_pide_sesion(client):
    assert client.get(PRONOSTICO).status_code in (401, 403)


def test_un_comprador_no_ve_el_pronostico(client, comprador):
    assert como(client, comprador).get(PRONOSTICO).status_code == 403
