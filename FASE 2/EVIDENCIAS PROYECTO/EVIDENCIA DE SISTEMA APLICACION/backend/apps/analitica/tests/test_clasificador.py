"""
El clasificador de la segmentación.

Lo que más importa probar acá no es que el modelo acierte, sino que **no haga
trampa**. Un modelo que ve el futuro al entrenar sale con métricas excelentes
y no sirve para nada al usarlo. Por eso la mayoría de estas pruebas fijan los
bordes: qué compras entran a las variables, cuáles a la etiqueta, y que la
prueba siempre quede después de todo lo usado para entrenar.
"""

from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from apps.analitica import clasificador as k

CORTE = date(2026, 3, 1)


def compra(hace, monto=10_000):
    """Una compra hecha `hace` días antes del corte (negativo: después)."""
    return (CORTE - timedelta(days=hace), monto)


# ── Las variables solo miran hacia atrás ────────────────────────────────────


def test_las_compras_posteriores_al_corte_no_cambian_las_variables():
    """
    Es la trampa clásica. Si una compra posterior al corte moviera la
    recencia o la frecuencia, el modelo estaría aprendiendo con la respuesta.
    """
    antes = [compra(40), compra(10)]
    con_futuro = antes + [compra(-5), compra(-60, 999_999)]

    assert k.variables(con_futuro, CORTE) == k.variables(antes, CORTE)


def test_variables_de_un_cliente_con_historia():
    historia = [compra(100, 20_000), compra(40, 10_000), compra(10, 30_000)]
    fila = k.variables(historia, CORTE)

    assert fila["recencia"] == 10
    assert fila["frecuencia"] == 3
    assert fila["monto"] == 60_000
    assert fila["ticket_promedio"] == 20_000
    assert fila["antiguedad"] == 100
    assert fila["dias_entre_compras"] == 45
    assert fila["compras_ultimos_90"] == 2


def test_quien_compro_una_vez_usa_su_antiguedad_como_intervalo():
    """Sin segunda compra no hay intervalo; lo que se sabe es cuánto lleva."""
    fila = k.variables([compra(30)], CORTE)

    assert fila["dias_entre_compras"] == 30


def test_quien_todavia_no_compraba_no_es_cliente_de_ese_corte():
    assert k.variables([compra(-10)], CORTE) is None


# ── La etiqueta solo mira hacia adelante ────────────────────────────────────


@pytest.mark.parametrize(
    ("hace", "esperado"),
    [
        (0, False),  # el mismo día del corte ya es pasado
        (-1, True),
        (-104, True),  # el último día del plazo cuenta
        (-105, False),
    ],
)
def test_bordes_de_la_etiqueta(hace, esperado):
    assert k.vuelve([compra(50), compra(hace)], CORTE, 104) is esperado


# ── El conjunto y la regla ──────────────────────────────────────────────────


def test_el_umbral_de_la_regla_se_calcula_con_lo_conocido_al_corte():
    """
    La regla tampoco puede ver el futuro. Si su umbral saliera de toda la
    historia, la línea base tendría una ventaja que el modelo no tiene y la
    comparación dejaría de ser justa.
    """
    pasado = {f"C{i}": [compra(200), compra(190)] for i in range(25)}
    futuro = {f"C{i}": hechas + [compra(-100)] for i, hechas in pasado.items()}

    sin = k.armar_conjunto(pasado, CORTE, 104)
    con = k.armar_conjunto(futuro, CORTE, 104)

    assert sin.umbrales == con.umbrales
    assert sin.filas == con.filas
    assert sin.etiquetas != con.etiquetas


def test_la_regla_predice_que_vuelve_quien_esta_dentro_del_umbral():
    conjunto = k.Conjunto(
        filas=[{"recencia": 30}, {"recencia": 104}, {"recencia": 105}],
        etiquetas=[1, 0, 0],
        umbrales=[104, 104, 104],
    )

    assert k.regla(conjunto) == [1, 1, 0]


def test_metricas_de_la_clase_vuelve():
    m = k.metricas([1, 1, 0, 0, 1], [1, 0, 1, 0, 1])

    assert m["verdaderos_positivos"] == 2
    assert m["falsos_positivos"] == 1
    assert m["falsos_negativos"] == 1
    assert m["precision"] == pytest.approx(2 / 3)
    assert m["exhaustividad"] == pytest.approx(2 / 3)
    assert m["f1"] == pytest.approx(2 / 3)


def test_decir_que_nadie_vuelve_da_cero_y_no_un_numero_alto():
    """Es la razón de medir sobre «vuelve»: el atajo no se ve bien."""
    assert k.metricas([0, 0, 0, 1], [0, 0, 0, 0])["f1"] == 0


def test_sin_diferencia_el_intervalo_es_cero():
    reales = [1, 0, 1, 0, 0, 1]
    pred = [1, 0, 0, 0, 1, 1]

    assert k.intervalo_de_la_diferencia(reales, pred, pred, veces=50) == (0, 0)


# ── El protocolo ────────────────────────────────────────────────────────────


def historia_sintetica(clientes=120, meses=15):
    """
    Una tienda con clientes que compran a ritmos distintos durante 15 meses.

    Fija y sin azar, para que la prueba dé lo mismo en cada corrida.
    """
    inicio = date(2025, 8, 1)
    compras = {}
    for i in range(clientes):
        cada = 20 + (i % 9) * 25
        primera = inicio + timedelta(days=(i * 7) % 200)
        fechas, f = [], primera
        while f < inicio + timedelta(days=30 * meses):
            fechas.append((f, 10_000 + 1_000 * (i % 5)))
            f += timedelta(days=cada if i % 3 else cada * 4)
        compras[f"Cliente {i:04d}"] = fechas
    return compras


def test_la_prueba_queda_despues_de_todo_lo_usado_para_entrenar():
    informe = k.evaluar(historia_sintetica(), 60)
    plazo = timedelta(days=60)

    assert informe.cortes_de_entrenamiento[-1] + plazo <= informe.corte_de_prueba
    assert informe.corte_de_validacion in informe.cortes_de_entrenamiento
    assert set(informe.modelos) == {"regresión logística", "XGBoost"}
    assert informe.elegido in informe.modelos
    assert 0.05 <= informe.umbral_de_probabilidad <= 0.95


def test_sin_historia_suficiente_no_se_inventa_una_evaluacion():
    corta = {"A": [(date(2026, 1, 1), 1000), (date(2026, 2, 1), 1000)]}

    with pytest.raises(ValueError, match="historia suficiente"):
        k.evaluar(corta, 104)


# ── El comando ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_el_comando_rechaza_una_tienda_que_no_existe():
    with pytest.raises(CommandError, match="No existe"):
        call_command("entrenar_segmentacion", "no-existe", stdout=StringIO())


@pytest.mark.django_db
def test_el_comando_avisa_si_la_tienda_no_tiene_historia(tienda_a, tmp_path):
    with pytest.raises(CommandError, match="historia suficiente"):
        call_command(
            "entrenar_segmentacion",
            tienda_a.slug,
            carpeta=str(tmp_path),
            stdout=StringIO(),
        )
