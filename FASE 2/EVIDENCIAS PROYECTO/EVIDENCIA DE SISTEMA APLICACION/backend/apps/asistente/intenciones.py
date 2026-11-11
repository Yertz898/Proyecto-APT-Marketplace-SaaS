"""
Qué puede preguntar el vendedor, y cómo se le responde.

**El modelo de lenguaje nunca ve los datos de la tienda.** Esa es la decisión
de diseño que sostiene todo lo demás. Lo único que hace —cuando hay modelo
configurado— es mirar la pregunta y decir a cuál de estas intenciones se
parece. La respuesta la arma este módulo, leyendo la base con el filtro de
tienda de siempre.

Lo que eso compra:

- **Una instrucción inyectada en la pregunta no tiene a qué acceder.** El peor
  caso es que la clasificación salga mal y el vendedor reciba la respuesta a
  otra pregunta sobre su propia tienda. No hay forma de que el asistente
  cuente datos de otra tienda, porque nunca los tuvo a la vista.
- **No puede inventar.** Las cifras salen de las mismas funciones que pintan
  el panel, así que el asistente y las pantallas no se pueden contradecir.
- **Funciona sin modelo.** Sin clave de API la clasificación es por palabras
  clave. Responde menos variantes de la misma pregunta, pero responde.

Lo que el asistente **no** hace: conversar. No tiene memoria, no opina y no
responde nada que no esté en esta lista. Cuando no entiende, lo dice y
enumera lo que sí sabe contestar.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from apps.analitica import pronostico as modulo_pronostico
from apps.analitica import segmentos as modulo_segmentos
from apps.analitica import ventas as modulo_ventas

#: Cuántos productos o clientes se nombran en una respuesta.
#:
#: Tres: una respuesta de chat se lee de corrido, y una lista de veinte
#: nombres no se lee, se saltea. Para la lista completa están las pantallas.
CUANTOS_NOMBRAR = 3


@dataclass(frozen=True)
class Respuesta:
    """
    Lo que el asistente contesta.

    `intencion` viaja para que la pantalla pueda ofrecer «ver el detalle» y
    llevar a la sección que corresponde, en vez de repetir la tabla entera
    dentro del chat.
    """

    intencion: str
    texto: str
    #: A qué sección del panel lleva el detalle, si corresponde.
    seccion: str | None = None


def responder(tienda, intencion: str, hoy: date | None = None) -> Respuesta:
    """Arma la respuesta de una intención ya clasificada."""
    constructor = RESPUESTAS.get(intencion, _no_entendi)
    return constructor(tienda, hoy or date.today())


# ── Las respuestas ──────────────────────────────────────────────────────────


def _ventas_del_mes(tienda, hoy) -> Respuesta:
    datos = modulo_ventas.resumen(tienda)
    cifras = datos["ventas"]

    if cifras["pedidos"] == 0:
        return Respuesta(
            "ventas_del_mes",
            f"En {datos['mes']['etiqueta']} todavía no tienes ventas confirmadas. "
            f"El mes anterior cerraste con {_pesos(datos['mesAnterior']['total'])}.",
            "ventas",
        )

    texto = (
        f"En {datos['mes']['etiqueta']} llevas {_pesos(cifras['total'])} "
        f"en {_plural(cifras['pedidos'], 'pedido', 'pedidos')}."
    )

    variacion = datos["mesAnterior"]["variacion"]
    if variacion is not None:
        rumbo = "más" if variacion >= 0 else "menos"
        texto += f" Es un {abs(round(variacion * 100))}% {rumbo} que el mes anterior."

    pendientes = datos["porCoordinar"]
    if pendientes["pedidos"]:
        texto += (
            f" Además tienes {_plural(pendientes['pedidos'], 'pedido', 'pedidos')} "
            f"por coordinar, por {_pesos(pendientes['total'])}."
        )

    return Respuesta("ventas_del_mes", texto, "ventas")


def _mas_vendidos(tienda, hoy) -> Respuesta:
    mejores = modulo_ventas.resumen(tienda)["masVendidos"][:CUANTOS_NOMBRAR]

    if not mejores:
        return Respuesta(
            "mas_vendidos",
            "Todavía no tienes ventas en los últimos 90 días, así que no hay "
            "nada que ordenar.",
            "ventas",
        )

    lista = _enumerar(f"{p['nombre']} ({_pesos(p['neto'])})" for p in mejores)
    return Respuesta(
        "mas_vendidos",
        f"En los últimos 90 días lo que más te dejó fue {lista}. "
        "Está ordenado por dinero, no por unidades.",
        "ventas",
    )


def _sin_movimiento(tienda, hoy) -> Respuesta:
    detenidos = modulo_ventas.resumen(tienda)["sinMovimiento"][:CUANTOS_NOMBRAR]

    if not detenidos:
        return Respuesta(
            "sin_movimiento",
            "Todo lo que llevas publicado hace más de 90 días se ha vendido al "
            "menos una vez.",
            "ventas",
        )

    return Respuesta(
        "sin_movimiento",
        "Llevan más de 90 días sin venderse: "
        f"{_enumerar(p['nombre'] for p in detenidos)}.",
        "ventas",
    )


def _por_coordinar(tienda, hoy) -> Respuesta:
    pendientes = modulo_ventas.resumen(tienda)["porCoordinar"]

    if not pendientes["pedidos"]:
        return Respuesta(
            "por_coordinar", "No tienes pedidos pendientes de coordinar.", "pedidos"
        )

    cuantos = _plural(pendientes["pedidos"], "pedido pendiente", "pedidos pendientes")
    return Respuesta(
        "por_coordinar",
        f"Tienes {cuantos} por {_pesos(pendientes['total'])}. El pago se coordina "
        "contigo, así que todavía no cuentan como venta.",
        "pedidos",
    )


def _pronostico(tienda, hoy) -> Respuesta:
    proyecciones = [p for p in modulo_pronostico.proyectar(tienda, hoy) if p.suficiente]

    if not proyecciones:
        return Respuesta(
            "pronostico",
            "Todavía no puedo proyectar nada: hacen falta "
            f"{modulo_pronostico.MINIMO_DE_MESES} meses con ventas de un mismo "
            "producto y ninguno los tiene. Con menos, el número diría más sobre "
            "el azar que sobre tu negocio.",
            "pronostico",
        )

    mejores = sorted(proyecciones, key=lambda p: -(p.esperado or 0))[:CUANTOS_NOMBRAR]
    lista = _enumerar(
        f"{p.nombre}, unos {_cantidad(p.esperado, p.unidad)}" for p in mejores
    )
    return Respuesta(
        "pronostico",
        f"Para el próximo mes espero {lista}. Es una estimación con "
        f"{mejores[0].metodo}, no una medición.",
        "pronostico",
    )


def _quiebre(tienda, hoy) -> Respuesta:
    proyecciones = modulo_pronostico.proyectar(tienda, hoy)
    por_agotarse = [
        p
        for p in proyecciones
        if p.dias_hasta_quiebre is not None and p.dias_hasta_quiebre <= 30
    ]

    if not any(p.suficiente for p in proyecciones):
        return Respuesta(
            "quiebre",
            "No puedo avisarte de quiebres todavía: sin pronóstico no sé a qué "
            "ritmo se vende, y sin eso no se puede decir cuándo se acaba.",
            "pronostico",
        )

    if not por_agotarse:
        return Respuesta(
            "quiebre",
            "Nada se te acaba en los próximos 30 días al ritmo actual.",
            "pronostico",
        )

    lista = _enumerar(
        f"{p.nombre} (unos {p.dias_hasta_quiebre} días)"
        for p in por_agotarse[:CUANTOS_NOMBRAR]
    )
    return Respuesta("quiebre", f"Se te va a acabar pronto: {lista}.", "pronostico")


def _clientes_en_riesgo(tienda, hoy) -> Respuesta:
    resumen = modulo_segmentos.segmentar(tienda, hoy)
    en_riesgo = [
        c for c in resumen.clientes if c.segmento == modulo_segmentos.Segmento.EN_RIESGO
    ]

    if not en_riesgo:
        return Respuesta(
            "clientes_en_riesgo",
            "No tienes clientes en riesgo: nadie que te compraba dejó de hacerlo.",
            "segmentos",
        )

    lista = _enumerar(
        f"{c.nombre} ({_pesos(c.monto)}, hace {c.recencia} días)"
        for c in en_riesgo[:CUANTOS_NOMBRAR]
    )
    return Respuesta(
        "clientes_en_riesgo",
        f"Tienes {len(en_riesgo)} clientes que te compraban y dejaron de hacerlo. "
        f"Los que más gastaron: {lista}. Cuento como «dejó de comprar» a quien "
        f"lleva más de {resumen.umbral} días sin volver.",
        "segmentos",
    )


def _clientes_habituales(tienda, hoy) -> Respuesta:
    resumen = modulo_segmentos.segmentar(tienda, hoy)
    conteo = resumen.conteo

    if not resumen.clientes:
        return Respuesta(
            "clientes_habituales",
            "Todavía no tienes compradores que agrupar.",
            "segmentos",
        )

    return Respuesta(
        "clientes_habituales",
        f"Tienes {conteo['habitual']} clientes habituales, {conteo['nuevo']} nuevos, "
        f"{conteo['en_riesgo']} en riesgo y {conteo['perdido']} perdidos.",
        "segmentos",
    )


def _no_entendi(tienda, hoy) -> Respuesta:
    return Respuesta(
        "no_entendi",
        "No entendí la pregunta. Puedo contarte cómo van tus ventas del mes, "
        "qué productos te dejaron más, cuáles llevan tiempo sin venderse, qué "
        "pedidos tienes por coordinar, cuánto espero que vendas el próximo mes, "
        "qué se te va a acabar y quiénes de tus clientes dejaron de comprar.",
    )


#: Qué responde cada intención.
RESPUESTAS = {
    "ventas_del_mes": _ventas_del_mes,
    "mas_vendidos": _mas_vendidos,
    "sin_movimiento": _sin_movimiento,
    "por_coordinar": _por_coordinar,
    "pronostico": _pronostico,
    "quiebre": _quiebre,
    "clientes_en_riesgo": _clientes_en_riesgo,
    "clientes_habituales": _clientes_habituales,
    "no_entendi": _no_entendi,
}

#: Cómo se le describe cada intención a la persona y al clasificador.
#:
#: El mismo texto sirve para las dos cosas a propósito: si el modelo y la
#: pantalla describieran las intenciones distinto, el asistente contestaría
#: cosas que la pantalla no ofrece.
DESCRIPCION = {
    "ventas_del_mes": "Cómo van mis ventas este mes",
    "mas_vendidos": "Qué productos me dejaron más",
    "sin_movimiento": "Qué llevo sin vender",
    "por_coordinar": "Qué pedidos tengo pendientes",
    "pronostico": "Cuánto voy a vender el próximo mes",
    "quiebre": "Qué se me va a acabar",
    "clientes_en_riesgo": "Qué clientes dejaron de comprarme",
    "clientes_habituales": "Cómo se reparten mis clientes",
}


# ── Auxiliares de redacción ─────────────────────────────────────────────────


def _pesos(monto) -> str:
    return f"${int(monto):,}".replace(",", ".")


def _cantidad(valor: Decimal, unidad: str) -> str:
    numero = f"{valor:,.0f}".replace(",", ".")
    return numero if unidad == "unidad" else f"{numero} {unidad}"


def _plural(cuantos: int, singular: str, plural: str) -> str:
    return f"{cuantos} {singular if cuantos == 1 else plural}"


def _enumerar(partes) -> str:
    """«a, b y c». Con la «y» antes del último, como se habla."""
    partes = list(partes)
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + " y " + partes[-1]
