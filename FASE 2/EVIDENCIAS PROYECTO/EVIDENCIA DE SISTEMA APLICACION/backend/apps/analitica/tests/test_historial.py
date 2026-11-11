"""
El lector de la planilla del cliente.

La planilla real no se puede usar en las pruebas: son ventas de personas con
nombre y apellido y el repositorio es público. Así que acá se arman planillas
de mentira **con las mismas deformaciones que tiene la de verdad**, que son
las que rompen a un lector ingenuo:

- Varios bloques de columnas en la misma hoja, uno al lado del otro.
- Bloques que empiezan en filas distintas.
- Encabezados repetidos dentro del mismo bloque.
- Cada versión le puso otro nombre a la columna del monto.
- Filas de plantilla con fecha y sin venta.

Cada una de esas apareció de verdad en el archivo del cliente.
"""

import datetime as dt
import io

import pytest
from openpyxl import Workbook

from apps.analitica import historial

#: Un bloque por gramo como el de 2025: tres tramos y el monto al final.
COLUMNAS = [
    "Fecha",
    "Descripcion",
    "Nombre",
    "Valor X G",
    "Valor X G",
    "Valor X G",
    "Total G X 430",
    "Total G X 580",
    "Total G X 1300",
    "Monto Bruto",
]


def planilla(hojas: dict) -> io.BytesIO:
    """
    Un .xlsx en memoria. `hojas` es {nombre: [(fila, columna, valor), ...]}.

    Se escribe celda por celda porque lo que se prueba es justamente que el
    lector encuentre bloques puestos en cualquier parte de la hoja.
    """
    libro = Workbook()
    libro.remove(libro.active)
    for nombre, celdas in hojas.items():
        hoja = libro.create_sheet(nombre)
        for fila, columna, valor in celdas:
            hoja.cell(row=fila, column=columna, value=valor)

    memoria = io.BytesIO()
    libro.save(memoria)
    memoria.seek(0)
    return memoria


def bloque(fila, columna, encabezados, filas):
    """Las celdas de un bloque: sus encabezados y sus filas de datos."""
    celdas = [(fila, columna + i, nombre) for i, nombre in enumerate(encabezados)]
    for salto, datos in enumerate(filas, start=1):
        celdas += [(fila + salto, columna + i, valor) for i, valor in enumerate(datos)]
    return celdas


UNA_VENTA = [
    dt.datetime(2025, 3, 14),
    "PUL",
    "Ana Soto",
    430,
    580,
    1300,
    None,
    20,
    None,
    24000,
]


def test_lee_una_venta_simple():
    archivo = planilla({"V2025": bloque(1, 1, COLUMNAS, [UNA_VENTA])})

    lectura = historial.leer(archivo)

    assert len(lectura.ventas) == 1
    venta = lectura.ventas[0]
    assert venta.fecha == dt.date(2025, 3, 14)
    assert venta.tipo == "PUL"
    assert venta.cliente == "Ana Soto"
    assert venta.monto == 24000
    assert venta.gramos == {580: 20}
    assert venta.por_gramo


def test_dos_bloques_lado_a_lado_no_se_mezclan():
    """
    El corte de un bloque es donde empieza el siguiente.

    Sin esto, el último bloque se lleva las columnas de los que vienen
    después y las ventas salen con los datos cruzados.
    """
    otra = [
        dt.datetime(2025, 4, 2),
        "CAD",
        "Luis Paz",
        430,
        580,
        1300,
        10,
        None,
        None,
        8000,
    ]
    archivo = planilla(
        {"V2025": bloque(1, 1, COLUMNAS, [UNA_VENTA]) + bloque(1, 11, COLUMNAS, [otra])}
    )

    lectura = historial.leer(archivo)

    assert [v.monto for v in lectura.ventas] == [24000, 8000]
    assert [v.gramos for v in lectura.ventas] == [{580: 20}, {430: 10}]


def test_bloques_que_empiezan_en_filas_distintas():
    """
    Pasa en la hoja de 2024: hay bloques con encabezado en la fila 1 y otros
    en la fila 8, porque se fueron agregando en momentos distintos.
    """
    tardio = [
        dt.datetime(2024, 9, 9),
        "AROS",
        "Eva Luz",
        430,
        580,
        1300,
        None,
        None,
        5,
        15000,
    ]
    archivo = planilla(
        {
            "V2024": bloque(1, 1, COLUMNAS, [UNA_VENTA])
            + bloque(8, 11, COLUMNAS, [tardio])
        }
    )

    lectura = historial.leer(archivo)

    assert sorted(v.monto for v in lectura.ventas) == [15000, 24000]


def test_los_encabezados_repetidos_no_se_pisan():
    """
    «Valor X G» aparece tres veces y «Total G X ...» otras tres. Sin numerar
    los repetidos, el diccionario de la fila se queda solo con el último y se
    pierden dos tramos de cada venta.
    """
    mixta = [
        dt.datetime(2025, 5, 1),
        "PUL + AROS",
        "Sol Vera",
        430,
        580,
        1300,
        12,
        8,
        4,
        50000,
    ]
    archivo = planilla({"V2025": bloque(1, 1, COLUMNAS, [mixta])})

    venta = historial.leer(archivo).ventas[0]

    assert venta.gramos == {430: 12, 580: 8, 1300: 4}


@pytest.mark.parametrize(
    "columna_de_monto", ["Monto Bruto", "Total Venta", "Valor total", "Ingreso"]
)
def test_el_monto_se_encuentra_con_cualquiera_de_sus_nombres(columna_de_monto):
    """Cada versión de la planilla le puso otro nombre a lo que pagó el comprador."""
    encabezados = COLUMNAS[:-1] + [columna_de_monto]
    archivo = planilla({"V2025": bloque(1, 1, encabezados, [UNA_VENTA])})

    assert historial.leer(archivo).ventas[0].monto == 24000


def test_una_fila_de_plantilla_no_es_una_venta():
    """
    La persona dejaba puestas la fecha y los precios por gramo en filas que
    después no usaba. Son ochenta en el archivo real.
    """
    vacia = [
        dt.datetime(2025, 6, 1),
        None,
        None,
        430,
        580,
        1300,
        None,
        None,
        None,
        None,
    ]
    archivo = planilla({"V2025": bloque(1, 1, COLUMNAS, [UNA_VENTA, vacia])})

    lectura = historial.leer(archivo)

    assert len(lectura.ventas) == 1
    assert lectura.descartes["fila de plantilla sin monto"] == 1


def test_una_fila_sin_fecha_se_anota_y_no_detiene_la_lectura():
    sin_fecha = ["TOTAL DEL MES", None, None, None, None, None, None, None, None, 99000]
    archivo = planilla({"V2025": bloque(1, 1, COLUMNAS, [sin_fecha, UNA_VENTA])})

    lectura = historial.leer(archivo)

    assert len(lectura.ventas) == 1
    assert lectura.descartes["sin fecha utilizable"] == 1


def test_una_venta_por_unidad_no_cuenta_como_venta_por_gramo():
    """
    Las de los primeros meses, cuando el negocio vendía piezas sueltas. Se
    leen igual —sirven para la serie de tiempo— pero no tienen producto en el
    catálogo de hoy, así que la importación las deja fuera.
    """
    encabezados = ["Fecha", "Descripcion", "Nombre", "Cantidad", "Valor total"]
    vieja = [dt.datetime(2024, 2, 10), "CADENA", "Rita Paz", 1, 20000]
    archivo = planilla({"V2024": bloque(1, 1, encabezados, [vieja])})

    venta = historial.leer(archivo).ventas[0]

    assert venta.monto == 20000
    assert venta.unidades == 1
    assert not venta.por_gramo


def test_las_ventas_salen_ordenadas_por_fecha():
    """Lo que se importa es una serie de tiempo; el orden del archivo no lo es."""
    tarde = [
        dt.datetime(2025, 12, 1),
        "PUL",
        "Z",
        430,
        580,
        1300,
        None,
        5,
        None,
        6000,
    ]
    temprano = [
        dt.datetime(2025, 1, 5),
        "PUL",
        "A",
        430,
        580,
        1300,
        None,
        5,
        None,
        6000,
    ]
    archivo = planilla({"V2025": bloque(1, 1, COLUMNAS, [tarde, temprano])})

    fechas = [v.fecha for v in historial.leer(archivo).ventas]

    assert fechas == sorted(fechas)


def test_una_hoja_que_falta_no_rompe_la_lectura():
    """El archivo lo manda el cliente y puede venir sin alguna hoja."""
    archivo = planilla({"V2025": bloque(1, 1, COLUMNAS, [UNA_VENTA])})

    lectura = historial.leer(archivo)

    assert len(lectura.ventas) == 1
    assert lectura.descartes["falta la hoja V2024"] == 1


def test_el_resumen_dice_el_rango_leido():
    archivo = planilla({"V2025": bloque(1, 1, COLUMNAS, [UNA_VENTA])})

    assert "2025-03-14" in historial.leer(archivo).resumen()


def test_todos_los_tramos_conocidos_apuntan_a_un_producto():
    """
    El mapeo es una tabla escrita a mano: si alguien agrega un tramo y olvida
    el producto, la importación de ese tramo se cae recién al correrla.
    """
    assert set(historial.PRODUCTO_POR_TRAMO.values()) == {
        "granel-hombre",
        "granel-mujer",
        "granel-colgantes-aros-anillos",
    }
