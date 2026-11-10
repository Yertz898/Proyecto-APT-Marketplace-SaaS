"""
Lee el libro de ventas que llevó el cliente y lo deja en una sola tabla.

Joyas_ye no tiene registro digital de sus ventas: lo único que existe es una
planilla que el dueño llevó a mano durante dos años. **El formato cambió
siete veces**, siguiendo al negocio: primero vendía piezas sueltas, después
lotes y hoy vende por gramo. Cada versión dejó su propio bloque de columnas,
puestos uno al lado del otro en la misma hoja, así que no hay una tabla que
leer: hay diecisiete.

Esto no corrige ni completa nada. Lee, normaliza los nombres de las columnas y
deja constancia de lo que no pudo leer. Si una fila está mala, se arregla acá
y se anota por qué, porque el archivo original es la única copia que existe de
esas ventas.

El archivo **no se versiona**: son ventas reales con nombres de personas que no
dieron permiso para publicarlos, y el repositorio es público. Vive en `data/`,
que está en .gitignore. Ver `data/README.md`.
"""

import datetime as dt
import re
from collections import Counter
from dataclasses import dataclass, field

from openpyxl import load_workbook

#: Dónde está la fila de encabezados en cada hoja con ventas.
#:
#: Son varias por hoja porque los bloques se fueron agregando en distintos
#: momentos y a distintas alturas. El que las escribió no estaba pensando en
#: que alguien las leyera con un programa.
HOJAS = {"V2025": [1], "V2024": [1, 3, 8, 9]}

#: Las columnas que traen gramos. El número es el costo por gramo de ese
#: tramo, y cambió varias veces en dos años.
COLUMNA_DE_GRAMOS = re.compile(r"^Total G X (\d+)(#\d+)?$")

#: Cada versión del libro le puso otro nombre a lo que pagó el comprador.
COLUMNAS_DE_MONTO = ("Monto Bruto", "Total Venta", "Valor total", "Ingreso")

#: A qué producto del catálogo corresponde cada tramo de costo.
#:
#: Sale de los datos y no de una suposición: tomando solo las ventas de un
#: único tramo, el precio por gramo que de verdad cobró fue ~$741 para los
#: tramos de 430 y 440, ~$1.000 para los de 560 a 650 y ~$1.900 para los de
#: 900 y 1300. Esos tres precios, sin IVA, son los $650, $900 y $1.500 de los
#: tres productos por gramo que la tienda tiene publicados hoy.
PRODUCTO_POR_TRAMO = {
    430: "granel-hombre",
    440: "granel-hombre",
    560: "granel-mujer",
    580: "granel-mujer",
    600: "granel-mujer",
    650: "granel-mujer",
    900: "granel-colgantes-aros-anillos",
    1300: "granel-colgantes-aros-anillos",
}


@dataclass
class Venta:
    """Una venta del libro, ya normalizada."""

    fecha: dt.date
    #: Lo que escribió el dueño: «PUL», «PUL + CAD», «LOTE PULSERAS».
    tipo: str
    #: El nombre tal como está en el libro. Se seudonimiza antes de guardarlo.
    cliente: str
    #: Gramos por tramo de costo: {430: 12.5, 1300: 4.0}.
    gramos: dict[int, float]
    #: Lo que pagó el comprador, con IVA.
    monto: int
    #: Unidades, en las ventas del formato viejo que no usaba gramos.
    unidades: float | None
    origen: str

    @property
    def por_gramo(self) -> bool:
        return bool(self.gramos)


@dataclass
class Lectura:
    ventas: list[Venta] = field(default_factory=list)
    descartes: Counter = field(default_factory=Counter)

    def resumen(self) -> str:
        if not self.ventas:
            return "No se leyó ninguna venta."
        fechas = [v.fecha for v in self.ventas]
        return (
            f"{len(self.ventas)} ventas entre {min(fechas)} y {max(fechas)}; "
            f"descartadas: {dict(self.descartes) or 'ninguna'}"
        )


def leer(ruta) -> Lectura:
    """Todas las ventas del libro, de todos sus formatos."""
    libro = load_workbook(ruta, data_only=True)
    lectura = Lectura()

    for nombre_hoja, filas_encabezado in HOJAS.items():
        if nombre_hoja not in libro.sheetnames:
            lectura.descartes[f"falta la hoja {nombre_hoja}"] += 1
            continue

        hoja = libro[nombre_hoja]
        for inicio, fin, fila_encabezado in _bloques(hoja, filas_encabezado):
            columnas = _nombres_de_columna(hoja, fila_encabezado, inicio, fin)
            for numero_fila in range(fila_encabezado + 1, hoja.max_row + 1):
                valores = [
                    hoja.cell(row=numero_fila, column=c).value
                    for c in range(inicio, fin)
                ]
                fila = dict(zip(columnas, valores, strict=True))
                _agregar(lectura, fila, f"{nombre_hoja}!c{inicio}")

    lectura.ventas.sort(key=lambda v: v.fecha)
    return lectura


def _bloques(hoja, filas_encabezado):
    """
    Dónde empieza y termina cada bloque de la hoja.

    Un bloque empieza donde una celda de encabezado dice «Fecha» y termina
    donde empieza el siguiente, **mirando todas las filas de encabezado a la
    vez**. Mirándolas por separado, el último bloque de una fila se come los
    bloques de la otra.
    """
    inicios = {}
    for fila in filas_encabezado:
        for celda in hoja[fila]:
            if isinstance(celda.value, str) and celda.value.strip().lower() == "fecha":
                inicios[celda.column] = fila

    columnas = sorted(inicios)
    for i, inicio in enumerate(columnas):
        fin = columnas[i + 1] if i + 1 < len(columnas) else hoja.max_column + 1
        yield inicio, fin, inicios[inicio]


def _nombres_de_columna(hoja, fila, desde, hasta) -> list[str]:
    """
    Los encabezados del bloque, numerando los repetidos.

    «Valor X G» aparece tres veces seguidas, una por tramo, y «Costo» otras
    tres. Sin numerarlos, el diccionario se quedaría solo con el último.
    """
    vistos: Counter = Counter()
    nombres = []
    for columna in range(desde, hasta):
        crudo = hoja.cell(row=fila, column=columna).value
        nombre = str(crudo).strip() if crudo is not None else ""
        vistos[nombre] += 1
        nombres.append(f"{nombre}#{vistos[nombre]}" if vistos[nombre] > 1 else nombre)
    return nombres


def _agregar(lectura: Lectura, fila: dict, origen: str) -> None:
    fecha = fila.get("Fecha")
    if not isinstance(fecha, dt.datetime):
        if any(v is not None for v in fila.values()):
            lectura.descartes["sin fecha utilizable"] += 1
        return

    monto = _primero_numerico(fila, COLUMNAS_DE_MONTO)
    if monto is None:
        # Casi todas son filas de plantilla: la persona dejó puesta la fecha y
        # los precios por gramo y nunca las usó. No hay venta que recuperar.
        lectura.descartes["fila de plantilla sin monto"] += 1
        return

    gramos = {}
    for clave, valor in fila.items():
        coincide = COLUMNA_DE_GRAMOS.match(clave or "")
        if coincide and isinstance(valor, (int, float)) and valor > 0:
            tramo = int(coincide.group(1))
            gramos[tramo] = gramos.get(tramo, 0) + float(valor)

    lectura.ventas.append(
        Venta(
            fecha=fecha.date(),
            tipo=_texto(fila.get("Descripcion")),
            cliente=_texto(fila.get("Nombre")),
            gramos=gramos,
            monto=round(monto),
            unidades=_numero(fila.get("Cantidad")),
            origen=origen,
        )
    )


def _primero_numerico(fila: dict, claves) -> float | None:
    for clave in claves:
        valor = _numero(fila.get(clave))
        if valor is not None:
            return valor
    return None


def _numero(valor) -> float | None:
    return float(valor) if isinstance(valor, (int, float)) else None


def _texto(valor) -> str:
    return str(valor).strip() if valor is not None else ""
