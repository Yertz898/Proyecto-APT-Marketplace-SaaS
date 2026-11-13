"""
Los modelos del pronóstico de demanda, medidos contra el promedio móvil.

El promedio móvil de `pronostico.py` es la línea base. Esto son los modelos que
tienen que ganarle; si no le ganan, no se integran (ver `docs/analitica.md`).

**Qué se pronostica.** La cantidad vendida de cada producto el mes siguiente,
con lo vendido hasta el mes anterior. Es exactamente lo que hace la pantalla.

**Cómo se mide, fijado antes de ver resultados.**

- Se recorre la serie mes a mes: para pronosticar un mes solo se usan los
  meses anteriores. Nunca se mezcla el orden: en una serie de tiempo, mezclar
  le muestra al modelo el futuro.
- Se pronostica desde el séptimo mes, porque la línea base no proyecta con
  menos de seis.
- Los primeros meses pronosticados son **validación**: ahí se elige el modelo
  y sus parámetros. Los últimos `MESES_DE_PRUEBA` son **prueba** y se miran
  una sola vez.
- La métrica que decide es el **MAPE**: es un porcentaje, así que permite
  juntar productos de escalas muy distintas. MAE y RMSE se reportan al lado,
  en la unidad del producto.

**Con quince meses no hay mucho que aprender**, y conviene decirlo antes del
resultado. Por eso los candidatos son pocos y simples, y por eso el resultado
lleva un intervalo de confianza.

Las librerías de aprendizaje se importan dentro de las funciones: la imagen de
producción no las instala.
"""

import math
import random
from dataclasses import dataclass
from itertools import product as combinaciones

# Holt vive en `pronostico.py` porque es el que usa la pantalla: así lo que se
# evalúa acá es exactamente lo que se muestra, y no una copia que puede
# divergir.
from apps.analitica.pronostico import MINIMO_DE_MESES, VENTANA, holt_amortiguado

#: Cuántos de los meses finales se reservan para la prueba.
#:
#: Cuatro meses por producto: doce pronósticos en Joyas_ye. Menos sería
#: decidir con un puñado de números; más dejaría a la validación sin con qué
#: elegir.
MESES_DE_PRUEBA = 4

REMUESTREOS = 1000


# ── Los pronosticadores ─────────────────────────────────────────────────────
#
# Todos reciben la historia de un producto —las cantidades de los meses
# anteriores, de la más vieja a la más nueva— y devuelven el pronóstico del mes
# siguiente. Ninguno ve el mes que pronostica.


def promedio_movil(historia: list[float], ventana: int = VENTANA) -> float:
    """La línea base, la misma de la pantalla."""
    ultimos = historia[-ventana:]
    return sum(ultimos) / len(ultimos)


def ultimo_mes(historia: list[float]) -> float:
    """
    Repetir el último mes. No es candidato: es la referencia más tonta posible.

    Si la línea base no le gana a esto, el problema es la línea base.
    """
    return historia[-1]


def tendencia_lineal(historia, meses) -> float:
    """
    Una recta sobre el logaritmo de los últimos `meses`, un paso adelante.

    En logaritmo para que la caída sea proporcional —perder un tercio cada
    tanto— y no en gramos fijos, que a la larga daría ventas negativas.
    """
    ys = [math.log1p(v) for v in historia[-meses:]]
    n = len(ys)
    xs = range(n)
    media_x, media_y = (n - 1) / 2, sum(ys) / n
    varianza = sum((x - media_x) ** 2 for x in xs)
    pendiente = (
        sum((x - media_x) * (y - media_y) for x, y in zip(xs, ys, strict=True))
        / varianza
        if varianza
        else 0.0
    )
    return max(math.expm1(media_y + pendiente * (n - media_x)), 0.0)


def _rasgos(historia: list[float]) -> list[float]:
    """
    Los tres últimos meses divididos por su promedio.

    Normalizado para que los tres productos, de escalas muy distintas, se
    puedan juntar en un solo modelo: con quince meses cada uno, por separado
    no alcanza para nada.
    """
    base = promedio_movil(historia) or 1.0
    return [v / base for v in historia[-VENTANA:]]


def xgboost_global(series_previas: list[list[float]], historia, **parametros):
    """
    Un solo XGBoost para todos los productos, entrenado con lo anterior.

    Aprende cuánto se aparta el mes siguiente de su promedio móvil según la
    forma de los tres meses previos, y lo aplica al producto que se
    pronostica. `series_previas` son las historias de todos los productos
    hasta el mismo mes, así que tampoco ve el futuro de los demás.
    """
    from xgboost import XGBRegressor

    x, y = [], []
    for serie in series_previas:
        for t in range(VENTANA, len(serie)):
            base = promedio_movil(serie[:t]) or 1.0
            x.append(_rasgos(serie[:t]))
            y.append(serie[t] / base)
    if len(x) < 5:
        return promedio_movil(historia)
    modelo = XGBRegressor(
        n_estimators=parametros.get("arboles", 100),
        max_depth=parametros.get("profundidad", 2),
        learning_rate=0.1,
        min_child_weight=2,
        random_state=7,
        n_jobs=1,
    )
    modelo.fit(x, y)
    razon = float(modelo.predict([_rasgos(historia)])[0])
    return max(razon * promedio_movil(historia), 0.0)


#: Los parámetros que se prueban en validación para cada candidato.
GRILLAS = {
    "Holt amortiguado": [
        {"alfa": a, "beta": b, "phi": p}
        for a, b, p in combinaciones((0.2, 0.4, 0.6, 0.8), (0.1, 0.2, 0.3), (0.8, 0.9))
    ],
    "tendencia lineal": [{"meses": m} for m in (4, 6, 9)],
    "XGBoost": [{"arboles": n, "profundidad": d} for n in (50, 100) for d in (1, 2)],
}


# ── Las métricas ────────────────────────────────────────────────────────────


def metricas(reales: list[float], pronosticos: list[float]) -> dict:
    """MAPE en porcentaje; MAE y RMSE en la unidad del producto."""
    pares = list(zip(reales, pronosticos, strict=True))
    errores = [abs(r - p) for r, p in pares]
    return {
        "mape": 100 * sum(abs(r - p) / r for r, p in pares if r) / len(pares),
        "mae": sum(errores) / len(pares),
        "rmse": math.sqrt(sum(e * e for e in errores) / len(pares)),
    }


def intervalo_de_la_diferencia(reales, modelo, base, veces=REMUESTREOS, semilla=7):
    """
    Cuánto puede variar la ventaja en MAPE del modelo sobre la línea base.

    Negativo es mejor: menos error. Si el intervalo incluye el cero, no se
    puede decir que el modelo gane. Con doce pronósticos, va a ser ancho.
    """
    azar = random.Random(semilla)
    n = len(reales)
    diferencias = []
    for _ in range(veces):
        idx = [azar.randrange(n) for _ in range(n)]
        r = [reales[i] for i in idx]
        diferencias.append(
            metricas(r, [modelo[i] for i in idx])["mape"]
            - metricas(r, [base[i] for i in idx])["mape"]
        )
    diferencias.sort()
    return diferencias[int(veces * 0.025)], diferencias[int(veces * 0.975) - 1]


# ── El protocolo ────────────────────────────────────────────────────────────


@dataclass
class Punto:
    """Un pronóstico: qué producto, qué mes y cuánto se vendió de verdad."""

    producto: str
    mes: str
    real: float
    #: El índice del mes en la serie: cuántos meses lo preceden.
    t: int
    prueba: bool


def puntos(series: dict[str, list[tuple[str, float]]]) -> list[Punto]:
    """Todos los meses pronosticables, marcando cuáles son de prueba."""
    resultado = []
    for codigo, serie in series.items():
        largo = len(serie)
        for t in range(MINIMO_DE_MESES, largo):
            resultado.append(
                Punto(codigo, serie[t][0], serie[t][1], t, t >= largo - MESES_DE_PRUEBA)
            )
    return resultado


def pronosticar(nombre, parametros, series, punto) -> float:
    """El pronóstico de un candidato para un punto, con solo lo anterior."""
    historia = [c for _, c in series[punto.producto][: punto.t]]
    if nombre == "promedio móvil":
        return promedio_movil(historia)
    if nombre == "último mes":
        return ultimo_mes(historia)
    if nombre == "Holt amortiguado":
        return holt_amortiguado(historia, **parametros)
    if nombre == "tendencia lineal":
        return tendencia_lineal(historia, **parametros)
    if nombre == "XGBoost":
        mes = series[punto.producto][punto.t][0]
        previas = [[c for m, c in serie if m < mes] for serie in series.values()]
        return xgboost_global(previas, historia, **parametros)
    raise ValueError(nombre)


@dataclass
class Informe:
    puntos_de_validacion: int
    puntos_de_prueba: int
    meses_de_prueba: list[str]
    linea_base: dict
    referencia: dict
    candidatos: dict
    elegido: str
    parametros: dict
    intervalo: tuple[float, float]
    detalle: list[dict]

    @property
    def gana(self) -> bool:
        """El elegido tiene menos error que la línea base, y no por azar."""
        return self.intervalo[1] < 0


def evaluar(series: dict[str, list[tuple[str, float]]]) -> Informe:
    """
    Elige en validación, mide una sola vez en prueba.

    `series` son los meses cerrados de cada producto con historia suficiente:
    {código: [(aaaa-mm, cantidad), ...]}, del más viejo al más nuevo.
    """
    series = {
        c: s for c, s in series.items() if len(s) > MINIMO_DE_MESES + MESES_DE_PRUEBA
    }
    if not series:
        raise ValueError(
            "No hay productos con historia suficiente para validar y probar por "
            f"separado: hacen falta más de {MINIMO_DE_MESES + MESES_DE_PRUEBA} meses."
        )
    todos = puntos(series)
    validacion = [p for p in todos if not p.prueba]
    prueba = [p for p in todos if p.prueba]

    def medir(nombre, parametros, conjunto):
        pron = [pronosticar(nombre, parametros, series, p) for p in conjunto]
        return metricas([p.real for p in conjunto], pron), pron

    # 1. Cada candidato elige sus parámetros en validación.
    elegidos = {}
    for nombre, grilla in GRILLAS.items():
        mejor = min(grilla, key=lambda g, n=nombre: medir(n, g, validacion)[0]["mape"])
        elegidos[nombre] = (mejor, medir(nombre, mejor, validacion)[0])
    elegido = min(elegidos, key=lambda n: elegidos[n][1]["mape"])

    # 2. Una sola medición en prueba, todos con sus parámetros ya fijos.
    reales = [p.real for p in prueba]
    base_m, base_p = medir("promedio móvil", {}, prueba)
    ref_m, _ = medir("último mes", {}, prueba)
    candidatos, pron_elegido = {}, None
    for nombre, (parametros, en_validacion) in elegidos.items():
        m, pron = medir(nombre, parametros, prueba)
        candidatos[nombre] = {
            "parametros": parametros,
            "validacion": en_validacion,
            "prueba": m,
        }
        if nombre == elegido:
            pron_elegido = pron

    detalle = [
        {
            "producto": p.producto,
            "mes": p.mes,
            "real": p.real,
            "promedio_movil": round(b, 1),
            "elegido": round(e, 1),
        }
        for p, b, e in zip(prueba, base_p, pron_elegido, strict=True)
    ]
    return Informe(
        puntos_de_validacion=len(validacion),
        puntos_de_prueba=len(prueba),
        meses_de_prueba=sorted({p.mes for p in prueba}),
        linea_base=base_m,
        referencia=ref_m,
        candidatos=candidatos,
        elegido=elegido,
        parametros=elegidos[elegido][0],
        intervalo=intervalo_de_la_diferencia(reales, pron_elegido, base_p),
        detalle=detalle,
    )
