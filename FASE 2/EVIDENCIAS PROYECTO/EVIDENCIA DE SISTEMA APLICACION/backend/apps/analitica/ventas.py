"""
Qué vendió la tienda. Hechos, no pronósticos.

Lo de acá se calcula sumando pedidos que ya existen. El pronóstico de demanda
y la segmentación son otra cosa, viven aparte y necesitan un modelo entrenado;
mezclarlos en la misma pantalla haría imposible saber qué número está medido y
cuál está estimado.

Tres decisiones que cambian todos los números y por eso van escritas acá:

1. **Un pedido pendiente todavía no es una venta.** El pago se coordina por
   WhatsApp fuera de la plataforma, así que entre que alguien confirma el
   pedido y paga puede no pasar nada. Se cuentan como venta los confirmados y
   los entregados; los pendientes se muestran aparte, como lo que falta
   coordinar.
2. **Un pedido anulado nunca cuenta**, ni siquiera en el mes en que se hizo.
3. **Los montos salen del pedido, no del catálogo.** Son los precios que se
   cobraron. Si se leyeran del producto, cambiar un precio reescribiría las
   ventas del mes pasado.
"""

from datetime import timedelta

from django.db.models import Count, Max, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.catalogo.models import Producto
from apps.pedidos.models import LineaPedido, Pedido

#: Qué estados cuentan como venta hecha.
VENDIDOS = (Pedido.Estado.CONFIRMADO, Pedido.Estado.ENTREGADO)

#: Sobre cuántos días se miran los más vendidos y los que no se mueven.
#:
#: Un mes es poca ventana para una tienda mayorista que vende por lotes: un
#: lote que no se vendió en noviembre no es necesariamente un lote detenido.
#: Noventa días es un trimestre, que es como mira el negocio el cliente.
DIAS_DE_VENTANA = 90

#: Cuántos meses de historia muestra el gráfico de ventas.
#:
#: Doce: un año cerrado deja ver si lo de este mes es temporada o es un
#: cambio. Con seis, diciembre no tiene contra qué compararse.
MESES_DEL_GRAFICO = 12

#: Cuántos productos se listan en cada tabla de la pantalla.
CUANTOS_LISTAR = 5

MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def resumen(tienda, ahora=None) -> dict:
    """Todo lo que muestra la pantalla de ventas, en una consulta por bloque."""
    ahora = ahora or timezone.localtime()

    inicio_mes = _inicio_del_mes(ahora)
    inicio_mes_anterior = _inicio_del_mes(inicio_mes - timedelta(days=1))
    desde_ventana = ahora - timedelta(days=DIAS_DE_VENTANA)

    este_mes = _sumar(tienda, inicio_mes, ahora)
    mes_anterior = _sumar(tienda, inicio_mes_anterior, inicio_mes)

    pendientes = Pedido.objects.filter(
        tienda=tienda, estado=Pedido.Estado.PENDIENTE
    ).aggregate(pedidos=Count("id"), total=Sum("total"))

    return {
        "mes": {
            "etiqueta": f"{MESES[inicio_mes.month - 1]} de {inicio_mes.year}",
            "desde": inicio_mes.date().isoformat(),
        },
        "ventas": este_mes,
        "mesAnterior": {
            **mes_anterior,
            "variacion": _variacion(mes_anterior["total"], este_mes["total"]),
        },
        "porCoordinar": {
            "pedidos": pendientes["pedidos"] or 0,
            "total": int(pendientes["total"] or 0),
        },
        "serieMensual": serie_mensual(tienda, ahora),
        "diasDeVentana": DIAS_DE_VENTANA,
        "masVendidos": mas_vendidos(tienda, desde_ventana),
        "sinMovimiento": sin_movimiento(tienda, desde_ventana, ahora),
    }


def serie_mensual(tienda, ahora, meses=MESES_DEL_GRAFICO) -> list[dict]:
    """
    Cuánto se vendió cada mes, para el gráfico.

    Los meses sin ventas vienen igual, en cero. Si se omitieran, el gráfico
    uniría octubre con diciembre como si fueran consecutivos y una caída se
    vería como una línea plana.

    El mes en curso va incluido y marcado `enCurso`: va por la mitad, así que
    su columna siempre es más baja y sin el aviso parecería un desplome.
    """
    inicio = _inicio_del_mes(ahora)
    for _ in range(meses - 1):
        inicio = _inicio_del_mes(inicio - timedelta(days=1))

    vendidos = {
        fila["mes"].strftime("%Y-%m"): fila
        for fila in Pedido.objects.filter(
            tienda=tienda, estado__in=VENDIDOS, fecha_creacion__gte=inicio
        )
        .annotate(mes=TruncMonth("fecha_creacion"))
        .values("mes")
        .annotate(pedidos=Count("id"), total=Sum("total"))
    }

    serie, cursor = [], inicio
    mes_actual = _inicio_del_mes(ahora).strftime("%Y-%m")
    for _ in range(meses):
        clave = cursor.strftime("%Y-%m")
        fila = vendidos.get(clave)
        serie.append(
            {
                "mes": clave,
                "etiqueta": f"{MESES[cursor.month - 1][:3]} {cursor.year % 100:02d}",
                "pedidos": fila["pedidos"] if fila else 0,
                "total": int(fila["total"]) if fila else 0,
                "enCurso": clave == mes_actual,
            }
        )
        # Al día 28 de cualquier mes, sumar cuatro días siempre cae en el
        # siguiente, sin importar si el mes tiene 28, 30 o 31.
        cursor = _inicio_del_mes(cursor.replace(day=28) + timedelta(days=4))

    return serie


def mas_vendidos(tienda, desde, cuantos=CUANTOS_LISTAR) -> list[dict]:
    """
    Los que más dinero dejaron en la ventana, no los que más unidades salieron.

    Son cosas distintas y la tienda vende lotes de precios muy distintos: diez
    lotes de aros baratos no valen lo mismo que dos de plata colombiana, y el
    dueño reparte su atención por lo segundo.
    """
    filas = (
        LineaPedido.objects.filter(
            pedido__tienda=tienda,
            pedido__estado__in=VENDIDOS,
            pedido__fecha_creacion__gte=desde,
        )
        .values("producto__codigo", "producto__nombre")
        .annotate(neto=Sum("subtotal_neto"), cantidad=Sum("cantidad"))
        .order_by("-neto")[:cuantos]
    )

    return [
        {
            "codigo": fila["producto__codigo"],
            "nombre": fila["producto__nombre"],
            "neto": int(fila["neto"] or 0),
            "cantidad": str(fila["cantidad"] or 0),
        }
        for fila in filas
    ]


def sin_movimiento(tienda, desde, ahora, cuantos=CUANTOS_LISTAR) -> list[dict]:
    """
    Productos publicados que no se vendieron en la ventana.

    Se dejan fuera los que se publicaron dentro de la ventana: un lote que
    entró al catálogo la semana pasada no es un lote detenido, nunca tuvo
    tiempo. Marcarlo sería empujar al dueño a rebajar algo que todavía no se
    ofreció.
    """
    vendidos = set(
        LineaPedido.objects.filter(
            pedido__tienda=tienda,
            pedido__estado__in=VENDIDOS,
            pedido__fecha_creacion__gte=desde,
        ).values_list("producto_id", flat=True)
    )

    candidatos = (
        Producto.objects.publicadas_de(tienda)
        .filter(fecha_creacion__lt=desde)
        .exclude(pk__in=vendidos)
        .annotate(
            # La última vez que se vendió, alguna vez, para poder decir «hace
            # tanto» en vez de solo «no se movió». Los pedidos anulados no
            # cuentan: si contaran, un lote anulado parecería recién vendido.
            ultima_venta=Max(
                "lineas_pedido__pedido__fecha_creacion",
                filter=Q(lineas_pedido__pedido__estado__in=VENDIDOS),
            )
        )
        .order_by("fecha_creacion")[:cuantos]
    )

    detenidos = []
    for producto in candidatos:
        ultima = producto.ultima_venta
        detenidos.append(
            {
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "precioNeto": producto.precio_neto,
                # Días desde la última venta, o None si nunca se vendió. Son
                # dos situaciones distintas y la pantalla las dice distinto.
                "diasSinVender": (ahora - ultima).days if ultima else None,
                "enCatalogoDesde": producto.fecha_creacion.date().isoformat(),
            }
        )
    return detenidos


# ── Auxiliares ──────────────────────────────────────────────────────────────


def _inicio_del_mes(momento):
    """El primer instante del mes, en hora de Chile y no en UTC.

    Importa: a las 21:30 del 30 de noviembre en Chile ya es 1 de diciembre en
    UTC, y las ventas del mes se cortarían un día antes.
    """
    local = timezone.localtime(momento)
    return local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _sumar(tienda, desde, hasta) -> dict:
    cifras = Pedido.objects.filter(
        tienda=tienda,
        estado__in=VENDIDOS,
        fecha_creacion__gte=desde,
        fecha_creacion__lt=hasta,
    ).aggregate(
        pedidos=Count("id"),
        neto=Sum("total_neto"),
        iva=Sum("total_iva"),
        total=Sum("total"),
    )

    return {
        "pedidos": cifras["pedidos"] or 0,
        "neto": int(cifras["neto"] or 0),
        "iva": int(cifras["iva"] or 0),
        "total": int(cifras["total"] or 0),
    }


def _variacion(antes: int, ahora: int) -> float | None:
    """
    Cuánto cambió respecto del mes anterior, entre 0 y 1.

    Devuelve None si el mes anterior fue cero: no hay porcentaje que calcular
    contra la nada, y mostrar «+100%» donde antes no había ventas es inventar
    una comparación.
    """
    if antes <= 0:
        return None
    return round((ahora - antes) / antes, 4)
