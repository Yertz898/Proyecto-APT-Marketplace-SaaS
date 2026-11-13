"""
El clasificador de la segmentación: quién va a volver a comprar.

La regla por recencia de `segmentos.py` es la línea base. Esto es el modelo que
tiene que ganarle; si no le gana, no se integra (ver `docs/analitica.md`).

**Qué se predice.** Para cada cliente que ya compró, si vuelve a comprar en los
próximos `horizonte` días. El horizonte es el umbral de la tienda —104 días en
Joyas_ye—, el mismo plazo con que la regla decide quién «se fue», así que los
dos responden exactamente la misma pregunta.

**Por qué la clase positiva es «vuelve» y no «se va».** En Joyas_ye nueve de
cada diez clientes no vuelven dentro del plazo. Medido sobre «se va», decir que
todos se van ya da un F1 cercano a 0,95 y cualquier regla parece excelente.
Medido sobre «vuelve», ese mismo atajo da cero. Es también la pregunta que le
sirve al dueño: a quién le conviene escribir.

**Cómo se evita mirar el futuro.** Todo se arma con fechas de corte. Las
variables de un cliente salen solo de las compras hasta el corte; la etiqueta,
solo de las compras entre el corte y el corte más el horizonte. Y se prueba en
un corte posterior a todo lo que se usó para entrenar, nunca con filas
mezcladas al azar: con datos que cambian en el tiempo, mezclar al azar enseña
el futuro al modelo y el resultado no se repite al usarlo de verdad.

Las librerías de aprendizaje se importan dentro de las funciones: la imagen de
producción no las instala (ver `docs/despliegue.md`) y este módulo no puede
romper el arranque del backend.
"""

import math
import random
from dataclasses import dataclass, field
from datetime import date, timedelta

from apps.analitica import segmentos

#: Cada cuántos días se toma una fecha de corte para entrenar.
#:
#: Un mes. Más seguido, las muestras de cortes vecinos son casi el mismo
#: cliente con la recencia corrida unos días, y el modelo cree tener más datos
#: de los que tiene.
PASO_ENTRE_CORTES = 30

#: Historia mínima de la tienda antes del primer corte.
#:
#: Con menos de dos meses, casi todos los clientes tienen una sola compra y
#: las variables no distinguen a nadie.
HISTORIA_MINIMA = 60

#: Las variables, en el orden en que entran al modelo.
VARIABLES = [
    "recencia",
    "frecuencia",
    "monto",
    "ticket_promedio",
    "antiguedad",
    "dias_entre_compras",
    "compras_ultimos_90",
]

#: Veces que se remuestrea el corte de prueba para el intervalo de confianza.
REMUESTREOS = 1000


# ── Las variables y la etiqueta ─────────────────────────────────────────────


def variables(compras, corte: date) -> dict | None:
    """
    Las variables de un cliente vistas desde `corte`. Nada posterior entra.

    Devuelve None si el cliente todavía no había comprado: no es un cliente
    de esa fecha y no hay nada que predecir sobre él.
    """
    hasta = sorted((f, float(m)) for f, m in compras if f <= corte)
    if not hasta:
        return None
    fechas = [f for f, _ in hasta]
    frecuencia = len(hasta)
    monto = sum(m for _, m in hasta)
    antiguedad = (corte - fechas[0]).days
    return {
        "recencia": (corte - fechas[-1]).days,
        "frecuencia": frecuencia,
        "monto": monto,
        "ticket_promedio": monto / frecuencia,
        "antiguedad": antiguedad,
        # Para quien compró una vez no hay intervalo: se usa su antigüedad,
        # que es lo más que se sabe que lleva sin repetir.
        "dias_entre_compras": (
            (fechas[-1] - fechas[0]).days / (frecuencia - 1)
            if frecuencia > 1
            else antiguedad
        ),
        "compras_ultimos_90": sum(1 for f in fechas if (corte - f).days < 90),
    }


def vuelve(compras, corte: date, horizonte: int) -> bool:
    """Si compró en el plazo que sigue al corte. El día del corte no cuenta."""
    fin = corte + timedelta(days=horizonte)
    return any(corte < f <= fin for f, _ in compras)


@dataclass
class Conjunto:
    """Las filas de uno o varios cortes, listas para entrenar o evaluar."""

    filas: list[dict] = field(default_factory=list)
    etiquetas: list[int] = field(default_factory=list)
    #: El umbral que la regla habría usado en cada fila, calculado solo con
    #: lo conocido en su fecha de corte.
    umbrales: list[int] = field(default_factory=list)

    def matriz(self):
        return [[fila[v] for v in VARIABLES] for fila in self.filas]

    def __len__(self):
        return len(self.filas)

    def sumar(self, otro: Conjunto) -> Conjunto:
        return Conjunto(
            self.filas + otro.filas,
            self.etiquetas + otro.etiquetas,
            self.umbrales + otro.umbrales,
        )


def armar_conjunto(compras_por_cliente, corte: date, horizonte: int) -> Conjunto:
    """Una fila por cliente que ya había comprado al momento del corte."""
    conocidas = {
        nombre: [(f, m) for f, m in hechas if f <= corte]
        for nombre, hechas in compras_por_cliente.items()
    }
    umbral, _ = segmentos.umbral_de_abandono({n: h for n, h in conocidas.items() if h})
    conjunto = Conjunto()
    for hechas in compras_por_cliente.values():
        fila = variables(hechas, corte)
        if fila is None:
            continue
        conjunto.filas.append(fila)
        conjunto.etiquetas.append(int(vuelve(hechas, corte, horizonte)))
        conjunto.umbrales.append(umbral)
    return conjunto


def cortes(desde: date, hasta: date) -> list[date]:
    """Fechas de corte cada `PASO_ENTRE_CORTES` días, sin pasarse de `hasta`."""
    resultado, corte = [], desde
    while corte <= hasta:
        resultado.append(corte)
        corte += timedelta(days=PASO_ENTRE_CORTES)
    return resultado


# ── La línea base y las métricas ────────────────────────────────────────────


def regla(conjunto: Conjunto) -> list[int]:
    """
    La línea base, traducida a la misma pregunta.

    La regla de `segmentos.py` da por ido a quien pasó el umbral sin volver.
    Leída al revés, predice que vuelve quien todavía está dentro del umbral:
    los «habituales» y los «nuevos».
    """
    return [
        int(fila["recencia"] <= umbral)
        for fila, umbral in zip(conjunto.filas, conjunto.umbrales, strict=True)
    ]


def metricas(reales: list[int], predichos: list[int]) -> dict:
    """Precisión, exhaustividad y F1 de la clase «vuelve»."""
    vp = sum(1 for r, p in zip(reales, predichos, strict=True) if r and p)
    fp = sum(1 for r, p in zip(reales, predichos, strict=True) if not r and p)
    fn = sum(1 for r, p in zip(reales, predichos, strict=True) if r and not p)
    precision = vp / (vp + fp) if vp + fp else 0.0
    exhaustividad = vp / (vp + fn) if vp + fn else 0.0
    f1 = (
        2 * precision * exhaustividad / (precision + exhaustividad)
        if precision + exhaustividad
        else 0.0
    )
    return {
        "precision": precision,
        "exhaustividad": exhaustividad,
        "f1": f1,
        "verdaderos_positivos": vp,
        "falsos_positivos": fp,
        "falsos_negativos": fn,
    }


def intervalo_de_la_diferencia(reales, modelo, base, veces=REMUESTREOS, semilla=7):
    """
    Cuánto puede variar la ventaja del modelo sobre la regla, al 95%.

    Con pocos clientes que vuelven, un F1 cambia bastante con que acierte o
    falle a cinco personas. Se remuestrean los clientes del corte de prueba
    con reposición y se mira la diferencia de F1 en cada remuestreo. Si el
    intervalo incluye el cero, no se puede decir que el modelo gane.
    """
    azar = random.Random(semilla)
    n = len(reales)
    diferencias = []
    for _ in range(veces):
        idx = [azar.randrange(n) for _ in range(n)]
        r = [reales[i] for i in idx]
        diferencias.append(
            metricas(r, [modelo[i] for i in idx])["f1"]
            - metricas(r, [base[i] for i in idx])["f1"]
        )
    diferencias.sort()
    return diferencias[int(veces * 0.025)], diferencias[int(veces * 0.975) - 1]


# ── Los modelos ─────────────────────────────────────────────────────────────


def _transformar(matriz):
    """
    Logaritmo de los conteos, montos y días.

    Son variables con cola larga: un cliente que gastó dos millones no es
    cuarenta veces más «cliente» que uno que gastó cincuenta mil. Sin esto la
    regresión logística queda dominada por unos pocos valores extremos.
    """
    return [[math.log1p(max(v, 0)) for v in fila] for fila in matriz]


def candidatos():
    """Los modelos que se comparan, con su configuración fija."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import FunctionTransformer, StandardScaler
    from xgboost import XGBClassifier

    return {
        # Lineal y explicable: cada variable tiene un peso que se puede leer.
        "regresión logística": make_pipeline(
            FunctionTransformer(_transformar),
            StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=1000),
        ),
        # Árboles: capta combinaciones, como «compra seguido pero hace mucho
        # que no viene». Poco profundo a propósito, porque hay pocos clientes
        # que vuelven y un árbol hondo se los aprende de memoria.
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            eval_metric="logloss",
            random_state=7,
            n_jobs=1,
        ),
    }


def _ajustar(modelo, conjunto: Conjunto):
    from xgboost import XGBClassifier

    x, y = conjunto.matriz(), conjunto.etiquetas
    if isinstance(modelo, XGBClassifier):
        positivos = sum(y) or 1
        modelo.set_params(scale_pos_weight=(len(y) - positivos) / positivos)
    modelo.fit(x, y)
    return modelo


def _probabilidades(modelo, conjunto: Conjunto) -> list[float]:
    return [float(p) for p in modelo.predict_proba(conjunto.matriz())[:, 1]]


def mejor_umbral(reales, probabilidades) -> float:
    """
    El corte de probabilidad que da el mejor F1 en validación.

    Se elige en validación y queda fijo para la prueba. Elegirlo mirando la
    prueba sería ajustar el examen a la respuesta.
    """
    mejor, mejor_f1 = 0.5, -1.0
    for paso in range(5, 96):
        u = paso / 100
        f1 = metricas(reales, [int(p >= u) for p in probabilidades])["f1"]
        if f1 > mejor_f1:
            mejor, mejor_f1 = u, f1
    return mejor


# ── El protocolo completo ───────────────────────────────────────────────────


@dataclass
class Informe:
    horizonte: int
    corte_de_validacion: date
    corte_de_prueba: date
    cortes_de_entrenamiento: list[date]
    filas_de_entrenamiento: int
    clientes_en_prueba: int
    vuelven_en_prueba: int
    regla: dict
    modelos: dict
    elegido: str
    umbral_de_probabilidad: float
    intervalo: tuple[float, float]
    importancia: dict

    @property
    def gana(self) -> bool:
        """El modelo elegido le gana a la regla, y no por azar."""
        return self.intervalo[0] > 0


def evaluar(compras_por_cliente, horizonte: int) -> Informe:
    """
    Entrena, elige y prueba, en ese orden y sin volver atrás.

    1. **Prueba**: el último corte cuya etiqueta ya se puede conocer entera.
    2. **Entrenamiento**: los cortes cuya etiqueta termina antes de la prueba.
    3. **Validación**: el último de esos cortes. Con los anteriores se entrena
       cada candidato y con este se elige el modelo y su umbral.
    4. El elegido se vuelve a entrenar con todos los cortes de entrenamiento
       y se mide **una sola vez** en la prueba, junto a la regla.
    """
    fechas = sorted(f for hechas in compras_por_cliente.values() for f, _ in hechas)
    if not fechas:
        raise ValueError("No hay historia suficiente: la tienda no tiene ventas.")
    primera, ultima = fechas[0], fechas[-1]
    plazo = timedelta(days=horizonte)

    prueba = ultima - plazo
    disponibles = cortes(primera + timedelta(days=HISTORIA_MINIMA), prueba - plazo)
    if len(disponibles) < 3:
        raise ValueError(
            "No hay historia suficiente para entrenar, validar y probar por separado."
        )
    validacion = disponibles[-1]
    para_validar = [c for c in disponibles if c + plazo <= validacion]
    if not para_validar:
        raise ValueError("No hay cortes de entrenamiento anteriores a la validación.")

    def juntar(lista):
        total = Conjunto()
        for c in lista:
            total = total.sumar(armar_conjunto(compras_por_cliente, c, horizonte))
        return total

    entrenamiento_parcial = juntar(para_validar)
    conjunto_validacion = armar_conjunto(compras_por_cliente, validacion, horizonte)
    entrenamiento = juntar(disponibles)
    conjunto_prueba = armar_conjunto(compras_por_cliente, prueba, horizonte)

    # Elección en validación.
    en_validacion = {}
    for nombre, modelo in candidatos().items():
        _ajustar(modelo, entrenamiento_parcial)
        probs = _probabilidades(modelo, conjunto_validacion)
        umbral = mejor_umbral(conjunto_validacion.etiquetas, probs)
        en_validacion[nombre] = (
            umbral,
            metricas(conjunto_validacion.etiquetas, [int(p >= umbral) for p in probs]),
        )
    elegido = max(en_validacion, key=lambda n: en_validacion[n][1]["f1"])

    # Una sola medición en la prueba, con el umbral ya fijo.
    reales = conjunto_prueba.etiquetas
    base = regla(conjunto_prueba)
    resultados, predicciones, importancia = {}, {}, {}
    for nombre, modelo in candidatos().items():
        _ajustar(modelo, entrenamiento)
        umbral = en_validacion[nombre][0]
        pred = [int(p >= umbral) for p in _probabilidades(modelo, conjunto_prueba)]
        predicciones[nombre] = pred
        resultados[nombre] = {
            "validacion": en_validacion[nombre][1],
            "prueba": metricas(reales, pred),
            "umbral": umbral,
        }
        if nombre == elegido:
            importancia = _importancia(modelo)

    return Informe(
        horizonte=horizonte,
        corte_de_validacion=validacion,
        corte_de_prueba=prueba,
        cortes_de_entrenamiento=disponibles,
        filas_de_entrenamiento=len(entrenamiento),
        clientes_en_prueba=len(conjunto_prueba),
        vuelven_en_prueba=sum(reales),
        regla=metricas(reales, base),
        modelos=resultados,
        elegido=elegido,
        umbral_de_probabilidad=en_validacion[elegido][0],
        intervalo=intervalo_de_la_diferencia(reales, predicciones[elegido], base),
        importancia=importancia,
    )


def _importancia(modelo) -> dict:
    """Cuánto pesa cada variable en el modelo elegido, para poder explicarlo."""
    if hasattr(modelo, "feature_importances_"):
        valores = modelo.feature_importances_
    else:
        valores = modelo[-1].coef_[0]
    return {v: round(float(x), 4) for v, x in zip(VARIABLES, valores, strict=True)}


def entrenar_final(compras_por_cliente, horizonte: int, nombre: str):
    """
    El modelo para usar: entrenado con todos los cortes de etiqueta conocida.

    Ya no se reserva prueba: la medición se hizo en `evaluar`, y dejar fuera
    los meses más recientes sería entrenar al modelo con un negocio que ya no
    es el de hoy.
    """
    fechas = sorted(f for hechas in compras_por_cliente.values() for f, _ in hechas)
    plazo = timedelta(days=horizonte)
    todos = cortes(fechas[0] + timedelta(days=HISTORIA_MINIMA), fechas[-1] - plazo)
    conjunto = Conjunto()
    for c in todos:
        conjunto = conjunto.sumar(armar_conjunto(compras_por_cliente, c, horizonte))
    return _ajustar(candidatos()[nombre], conjunto)
