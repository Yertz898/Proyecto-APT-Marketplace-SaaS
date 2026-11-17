"""
La ficha de la tienda: los hechos con que el asistente responde lo que no
está en la lista de preguntas conocidas.

Cuando el vendedor pregunta algo que ninguna intención cubre —«¿cuánto vendí
ayer?», «¿cuántos productos tengo?», «¿cuál es mi producto más caro?»—, el
modelo no inventa: recibe esta ficha y redacta la respuesta **solo con lo que
está escrito acá**. Si el dato no está, lo dice.

Tres reglas:

- **La arma el backend, con el filtro de tienda de siempre.** El modelo no
  consulta nada; recibe un diccionario ya calculado. Una instrucción inyectada
  en la pregunta no tiene a qué acceder: lo peor que logra es que el modelo
  redacte mal cifras de la propia tienda.
- **Sin datos personales.** Ni nombres de clientes, ni correos, ni teléfonos,
  ni RUT: solo conteos y montos. Los productos sí van por nombre, porque son
  el catálogo público de la tienda.
- **Las mismas funciones que el panel.** Las ventas salen de
  `analitica.ventas`, el pronóstico de `analitica.pronostico` y los segmentos
  de `analitica.segmentos`, así que el asistente no puede contradecir a las
  pantallas.
"""

import re
from datetime import date, timedelta

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from apps.analitica import pronostico as modulo_pronostico
from apps.analitica import segmentos as modulo_segmentos
from apps.analitica import ventas as modulo_ventas
from apps.catalogo.models import Producto
from apps.pedidos.models import LineaPedido, Pedido

#: Cuántos productos van en cada lista de la ficha.
CUANTOS = 5

#: Tope de filas del historial diario y por producto. Una tienda pyme tiene
#: unos cientos de días con ventas al año; esto mantiene la ficha en unas
#: pocas miles de palabras aunque la tienda crezca.
TOPE_DE_FILAS = 400

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _producto(p) -> dict:
    return {
        "nombre": p.nombre,
        "precioNeto": p.precio_neto,
        "unidad": p.unidad_medida,
        "formaDeVenta": p.forma_venta,
    }


def _historial(tienda) -> dict:
    """
    Todas las ventas, agregadas por día, mes, año, día de la semana y producto.

    Es lo que permite contestar «¿cuánto vendí el 15 de diciembre?» o «¿qué día
    de la semana vendo más?». Son sumas de pedidos confirmados y entregados,
    los mismos que cuenta la pantalla de ventas.
    """
    vendidos = Pedido.objects.filter(tienda=tienda, estado__in=modulo_ventas.VENDIDOS)
    por_dia = list(
        vendidos.annotate(dia=TruncDate("fecha_creacion"))
        .values("dia")
        .annotate(pedidos=Count("id"), total=Sum("total"))
        .order_by("-dia")[:TOPE_DE_FILAS]
    )
    por_dia.reverse()

    por_mes, por_anio, por_semana = {}, {}, {d: [0, 0] for d in DIAS}
    semanas = {}
    todos = (
        vendidos.annotate(dia=TruncDate("fecha_creacion"))
        .values("dia")
        .annotate(pedidos=Count("id"), total=Sum("total"))
    )
    for fila in todos:
        total, pedidos = int(fila["total"] or 0), fila["pedidos"]
        lunes = fila["dia"] - timedelta(days=fila["dia"].weekday())
        for tabla, clave in (
            (
                semanas,
                f"{lunes.isoformat()} al {(lunes + timedelta(days=6)).isoformat()}",
            ),
            (por_mes, fila["dia"].strftime("%Y-%m")),
            (por_anio, str(fila["dia"].year)),
            (por_semana, DIAS[fila["dia"].weekday()]),
        ):
            tabla.setdefault(clave, [0, 0])
            tabla[clave][0] += pedidos
            tabla[clave][1] += total

    por_producto = (
        LineaPedido.objects.filter(pedido__in=vendidos)
        .annotate(mes=TruncMonth("pedido__fecha_creacion"))
        .values("mes", "producto__nombre", "producto__unidad_medida")
        .annotate(cantidad=Sum("cantidad"), neto=Sum("subtotal_neto"))
        .order_by("-mes", "-neto")[:TOPE_DE_FILAS]
    )

    cifras = vendidos.aggregate(pedidos=Count("id"), total=Sum("total"))
    pedidos, total = cifras["pedidos"] or 0, int(cifras["total"] or 0)

    def filas(tabla):
        return [
            _con_ticket({"periodo": k, "pedidos": v[0], "total": v[1]})
            for k, v in tabla.items()
        ]

    return {
        "primeraVenta": por_dia[0]["dia"].isoformat() if por_dia else None,
        "ultimaVenta": por_dia[-1]["dia"].isoformat() if por_dia else None,
        "pedidosEnTotal": pedidos,
        "totalVendido": total,
        "ticketPromedio": round(total / pedidos) if pedidos else None,
        "porAnio": filas(dict(sorted(por_anio.items()))),
        "porMes": filas(dict(sorted(por_mes.items()))),
        # Semanas de lunes a domingo, las últimas con ventas.
        "porSemana": filas(dict(sorted(semanas.items())[-TOPE_DE_FILAS:])),
        "porDiaDeLaSemana": filas(por_semana),
        "porDia": [
            {
                "fecha": f["dia"].isoformat(),
                "dia": DIAS[f["dia"].weekday()],
                "pedidos": f["pedidos"],
                "total": int(f["total"] or 0),
            }
            for f in por_dia
        ],
        "porProductoYMes": [
            {
                "mes": f["mes"].strftime("%Y-%m"),
                "producto": f["producto__nombre"],
                "cantidad": str(f["cantidad"].normalize()),
                "unidad": f["producto__unidad_medida"],
                "neto": int(f["neto"] or 0),
            }
            for f in por_producto
        ],
    }


MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

_FECHA_CON_MES = re.compile(
    r"\b(\d{1,2}) de (" + "|".join(MESES) + r")(?: (?:de |del )?(\d{4}))?\b"
)
_FECHA_CON_BARRAS = re.compile(r"\b(\d{1,2}) (\d{1,2})(?: (\d{4}))?\b")


def _fecha_pasada(dia: int, mes: int, anio: int | None, hoy: date) -> date | None:
    """La fecha, y si no dicen el año, la más reciente que no sea futura."""
    try:
        if anio:
            return date(anio, mes, dia)
        fecha = date(hoy.year, mes, dia)
        return fecha if fecha <= hoy else date(hoy.year - 1, mes, dia)
    except ValueError:
        return None


def fechas_de_la_pregunta(pregunta: str, hoy: date) -> list[date]:
    """
    Los días que nombra la pregunta, ya con su año.

    Lo resuelve el backend y no el modelo: en las pruebas, ante «¿qué vendí el 3
    de octubre?», el modelo eligió el año que sí tenía ventas en vez del último
    3 de octubre. Acepta «15 de diciembre (de 2025)», «15/12(/2025)», «hoy»,
    «ayer» y «anteayer». `pregunta` viene normalizada: sin tildes y con las
    barras convertidas en espacios.
    """
    fechas = []
    for dia, mes, anio in _FECHA_CON_MES.findall(pregunta):
        fechas.append(
            _fecha_pasada(int(dia), MESES[mes], int(anio) if anio else None, hoy)
        )
    for dia, mes, anio in _FECHA_CON_BARRAS.findall(pregunta):
        if 1 <= int(mes) <= 12:
            fechas.append(
                _fecha_pasada(int(dia), int(mes), int(anio) if anio else None, hoy)
            )
    palabras = set(pregunta.split())
    for palabra, dias in (("hoy", 0), ("ayer", 1), ("anteayer", 2)):
        if palabra in palabras:
            fechas.append(hoy - timedelta(days=dias))
    unicas = []
    for fecha in fechas:
        if fecha and fecha not in unicas:
            unicas.append(fecha)
    return unicas[:10]


_MES = "(" + "|".join(MESES) + ")"
_RANGO = re.compile(
    r"\b(?:entre el|entre|del|desde el) (\d{1,2})(?: de " + _MES + r")?"
    r" (?:y el|y|al|hasta el) (\d{1,2}) de " + _MES + r"(?: (?:de |del )?(\d{4}))?\b"
)


def rangos_de_la_pregunta(pregunta: str, hoy: date) -> list[tuple[date, date]]:
    """
    Los rangos de días que nombra la pregunta: «entre el 1 y el 10 de
    diciembre», «del 20 de noviembre al 5 de diciembre de 2025».

    También los resuelve el backend: sumar decenas de días a mano fue lo que
    el modelo hizo mal en las pruebas.
    """
    rangos = []
    for d1, m1, d2, m2, anio in _RANGO.findall(pregunta):
        hasta = _fecha_pasada(int(d2), MESES[m2], int(anio) if anio else None, hoy)
        if hasta is None:
            continue
        mes_desde = MESES[m1] if m1 else MESES[m2]
        anio_desde = hasta.year - (1 if mes_desde > hasta.month else 0)
        try:
            desde = date(anio_desde, mes_desde, int(d1))
        except ValueError:
            continue
        if desde <= hasta:
            rangos.append((desde, hasta))
    return rangos[:5]


def _con_ticket(cifras: dict) -> dict:
    """Agrega el ticket promedio, para que el modelo no tenga que dividir."""
    pedidos = cifras.get("pedidos") or 0
    total = cifras.get("total") or 0
    return {**cifras, "ticketPromedio": round(total / pedidos) if pedidos else None}


def _lo_mayor(filas: list[dict]) -> dict | None:
    con_ventas = [f for f in filas if f.get("total")]
    return max(con_ventas, key=lambda f: f["total"]) if con_ventas else None


def armar(tienda, hoy=None, pregunta: str = "") -> dict:
    """
    Los hechos de la tienda, listos para que el modelo los lea.

    Con `pregunta`, la ficha trae además las ventas de los días que nombra.
    """
    ahora = timezone.localtime()
    sumar = modulo_ventas._sumar
    hoy = hoy or ahora.date()
    inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)

    resumen = modulo_ventas.resumen(tienda, ahora)
    este_mes = resumen["ventas"]

    productos = Producto.objects.filter(tienda=tienda)
    conteo = productos.aggregate(
        total=Count("id"),
        publicados=Count("id", filter=Q(activo=True)),
        desactivados=Count("id", filter=Q(activo=False)),
        agotados=Count("id", filter=Q(activo=True, controla_stock=True, stock__lte=0)),
    )
    por_forma = dict(
        productos.filter(activo=True)
        .values_list("forma_venta")
        .annotate(n=Count("id"))
        .values_list("forma_venta", "n")
    )
    por_categoria = dict(
        productos.filter(activo=True, categoria__isnull=False)
        .values_list("categoria__nombre")
        .annotate(n=Count("id"))
        .values_list("categoria__nombre", "n")
    )
    activos = productos.filter(activo=True)
    caros = activos.order_by("-precio_neto")[:CUANTOS]
    baratos = activos.order_by("precio_neto")[:CUANTOS]
    con_stock = activos.filter(controla_stock=True, stock__gt=0)
    stock_bajo = con_stock.order_by("stock")[:CUANTOS]

    proyecciones = [p for p in modulo_pronostico.proyectar(tienda, hoy) if p.suficiente]
    segmentos = modulo_segmentos.segmentar(tienda, hoy)
    historial = _historial(tienda)
    agotados = activos.filter(controla_stock=True, stock__lte=0)
    categorias = sorted(por_categoria.items(), key=lambda c: -c[1])

    # Los días que nombra la pregunta, con su resultado ya buscado.
    por_fecha = {d["fecha"]: d for d in historial["porDia"]}
    dias_pedidos = [
        {
            "fecha": f.isoformat(),
            "dia": DIAS[f.weekday()],
            **_con_ticket(
                {
                    k: por_fecha.get(f.isoformat(), {}).get(k, 0)
                    for k in ("pedidos", "total")
                }
            ),
        }
        # Sin los rangos: «del 1 al 10 de diciembre» no es el día 10.
        for f in fechas_de_la_pregunta(_RANGO.sub(" ", pregunta), hoy)
    ]
    rangos_pedidos = []
    for desde, hasta in rangos_de_la_pregunta(pregunta, hoy):
        dentro = [
            d
            for d in historial["porDia"]
            if desde.isoformat() <= d["fecha"] <= hasta.isoformat()
        ]
        rangos_pedidos.append(
            _con_ticket(
                {
                    "desde": desde.isoformat(),
                    "hasta": hasta.isoformat(),
                    "pedidos": sum(d["pedidos"] for d in dentro),
                    "total": sum(d["total"] for d in dentro),
                    "diasConVentas": len(dentro),
                }
            )
        )

    return {
        "tienda": tienda.nombre,
        "hoy": hoy.isoformat(),
        "nota": (
            "Montos en pesos chilenos con IVA, salvo los campos «neto». Una venta "
            "es un pedido confirmado o entregado; los pendientes de coordinar van "
            "aparte. En historial.porDia solo están los días con ventas: un día "
            "entre primeraVenta y hoy que no aparece es un día sin ventas."
        ),
        "diasQueNombraLaPregunta": dias_pedidos,
        "rangosQueNombraLaPregunta": rangos_pedidos,
        "ventas": {
            "hoy": _con_ticket(sumar(tienda, inicio_hoy, ahora)),
            "ayer": _con_ticket(
                sumar(tienda, inicio_hoy - timedelta(days=1), inicio_hoy)
            ),
            "ultimos7Dias": _con_ticket(
                sumar(tienda, ahora - timedelta(days=7), ahora)
            ),
            "ultimos30Dias": _con_ticket(
                sumar(tienda, ahora - timedelta(days=30), ahora)
            ),
            "esteMes": _con_ticket({"mes": resumen["mes"]["etiqueta"], **este_mes}),
            "mesAnterior": _con_ticket(resumen["mesAnterior"]),
            "ticketPromedioHistorico": historial["ticketPromedio"],
        },
        "loMejor": {
            "dia": _lo_mayor(historial["porDia"]),
            "mes": _lo_mayor(historial["porMes"]),
            "anio": _lo_mayor(historial["porAnio"]),
            "diaDeLaSemana": _lo_mayor(historial["porDiaDeLaSemana"]),
            "categoriaConMasProductos": (
                {"categoria": categorias[0][0], "productos": categorias[0][1]}
                if categorias
                else None
            ),
        },
        "historial": historial,
        "pedidosPorCoordinar": resumen["porCoordinar"],
        "masVendidos90Dias": [
            {"nombre": p["nombre"], "neto": p["neto"], "cantidad": p["cantidad"]}
            for p in resumen["masVendidos"][:CUANTOS]
        ],
        "sinVenderHace90Dias": [
            {"nombre": p["nombre"], "diasSinVender": p["diasSinVender"]}
            for p in resumen["sinMovimiento"][:CUANTOS]
        ],
        "catalogo": {
            **conteo,
            "porFormaDeVenta": por_forma,
            # Ordenadas de más a menos productos: leer un diccionario
            # desordenado fue donde el modelo se equivocó en las pruebas.
            "porCategoria": [{"categoria": c, "productos": n} for c, n in categorias],
            "masCaros": [_producto(p) for p in caros],
            "masBaratos": [_producto(p) for p in baratos],
            "agotados": [p.nombre for p in agotados[:TOPE_DE_FILAS]],
            "conPocoStock": [
                {"nombre": p.nombre, "stock": str(p.stock), "unidad": p.unidad_medida}
                for p in stock_bajo
            ],
        },
        "pronosticoProximoMes": [
            {
                "nombre": p.nombre,
                "esperado": str(round(p.esperado or 0)),
                "unidad": p.unidad,
                "diasHastaQuedarseSinStock": p.dias_hasta_quiebre,
                "metodo": p.metodo,
            }
            for p in proyecciones
        ],
        "clientes": {
            "total": len(segmentos.clientes),
            "porSegmento": segmentos.conteo,
            "diasSinComprarParaEstarEnRiesgo": segmentos.umbral,
        },
    }
