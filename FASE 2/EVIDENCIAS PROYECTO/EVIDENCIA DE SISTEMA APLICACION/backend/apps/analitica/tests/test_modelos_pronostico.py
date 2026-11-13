"""
Los modelos del pronóstico.

Igual que en la segmentación, lo primero que se prueba es que **no hagan
trampa**: que ningún pronóstico vea el mes que pronostica, ni el futuro de
los otros productos, y que la prueba quede siempre al final de la serie.
Después, que cada pronosticador haga lo que dice su nombre.
"""

from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from apps.analitica import modelos_pronostico as m


def serie(valores, desde=(2025, 8)):
    """Una serie mensual con esas cantidades, desde ese mes."""
    anio, mes = desde
    resultado = []
    for v in valores:
        resultado.append((f"{anio}-{mes:02d}", float(v)))
        mes += 1
        if mes > 12:
            anio, mes = anio + 1, 1
    return resultado


# ── Ningún pronóstico ve el mes que pronostica ──────────────────────────────


@pytest.mark.parametrize(
    ("nombre", "parametros"),
    [
        ("promedio móvil", {}),
        ("último mes", {}),
        ("Holt amortiguado", {"alfa": 0.4, "beta": 0.1, "phi": 0.8}),
        ("tendencia lineal", {"meses": 6}),
        ("XGBoost", {"arboles": 50, "profundidad": 2}),
    ],
)
def test_cambiar_el_futuro_no_cambia_el_pronostico(nombre, parametros):
    """
    Si el mes pronosticado o los siguientes movieran el pronóstico, el modelo
    estaría leyendo la respuesta. Se cambian a valores absurdos y el
    pronóstico tiene que salir idéntico.
    """
    base = [100, 120, 90, 110, 130, 95, 105, 115, 100, 90, 85, 80]
    futuro = base[:8] + [99_999, 0, 50_000, 1]
    series = {"A": serie(base), "B": serie([v * 2 for v in base])}
    alteradas = {"A": serie(futuro), "B": serie([v * 2 for v in futuro])}
    punto = m.Punto("A", series["A"][8][0], base[8], 8, False)

    assert m.pronosticar(nombre, parametros, series, punto) == pytest.approx(
        m.pronosticar(nombre, parametros, alteradas, punto)
    )


def test_la_prueba_son_los_ultimos_meses_de_cada_producto():
    puntos = m.puntos({"A": serie(range(100, 115))})
    prueba = [p for p in puntos if p.prueba]

    assert [p.t for p in prueba] == [11, 12, 13, 14]
    assert all(p.t >= 6 for p in puntos)
    assert max(p.t for p in puntos if not p.prueba) < min(p.t for p in prueba)


# ── Cada pronosticador ──────────────────────────────────────────────────────


def test_promedio_movil_y_ultimo_mes():
    assert m.promedio_movil([10, 20, 30, 60]) == pytest.approx(110 / 3)
    assert m.ultimo_mes([10, 20, 30, 60]) == 60


def test_holt_sigue_una_serie_constante():
    assert m.holt_amortiguado([500] * 10, 0.4, 0.1, 0.8) == pytest.approx(500)


def test_holt_amortiguado_no_proyecta_la_caida_completa():
    """
    Con la tendencia amortiguada, una caída sostenida se proyecta más suave
    que su ritmo: es la diferencia con una recta, que la sigue igual hasta
    llegar a cero.
    """
    caida = [1000, 900, 800, 700, 600, 500]

    pronostico = m.holt_amortiguado(caida, 0.8, 0.3, 0.8)

    assert 400 < pronostico < 500


def test_ningun_pronostico_es_negativo():
    caida = [1000, 500, 200, 50, 10, 1]

    assert m.holt_amortiguado(caida, 0.8, 0.3, 0.9) >= 0
    assert m.tendencia_lineal(caida, 6) >= 0


def test_tendencia_lineal_sigue_una_caida_proporcional():
    """En logaritmo, perder la mitad cada mes da la mitad del último."""
    assert m.tendencia_lineal([800, 400, 200, 100], 4) == pytest.approx(50, rel=0.1)


def test_metricas():
    r = m.metricas([100, 200], [110, 150])

    assert r["mape"] == pytest.approx((10 + 25) / 2)
    assert r["mae"] == pytest.approx(30)
    assert r["rmse"] == pytest.approx(((100 + 2500) / 2) ** 0.5)


# ── El protocolo ────────────────────────────────────────────────────────────


def test_evaluar_elige_en_validacion_y_mide_en_prueba():
    series = {
        "A": serie([100, 120, 90, 110, 130, 95, 105, 115, 100, 90, 85, 80, 75, 70, 65]),
        "B": serie([50, 55, 60, 52, 58, 61, 57, 59, 62, 60, 58, 55, 54, 52, 50]),
    }

    informe = m.evaluar(series)

    assert informe.puntos_de_prueba == 8
    assert informe.puntos_de_validacion == 10
    assert informe.elegido in m.GRILLAS
    assert informe.parametros in m.GRILLAS[informe.elegido]
    assert len(informe.detalle) == 8


def test_sin_historia_suficiente_no_se_inventa_una_evaluacion():
    with pytest.raises(ValueError, match="historia suficiente"):
        m.evaluar({"A": serie(range(100, 108))})


@pytest.mark.django_db
def test_el_comando_rechaza_una_tienda_que_no_existe():
    with pytest.raises(CommandError, match="No existe"):
        call_command("entrenar_pronostico", "no-existe", stdout=StringIO())


@pytest.mark.django_db
def test_el_comando_avisa_si_la_tienda_no_tiene_historia(tienda_a, tmp_path):
    with pytest.raises(CommandError, match="historia suficiente"):
        call_command(
            "entrenar_pronostico",
            tienda_a.slug,
            carpeta=str(tmp_path),
            stdout=StringIO(),
        )
