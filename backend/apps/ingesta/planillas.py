"""
Leer una planilla hecha a mano.

Este módulo existe porque el archivo lo escribe una persona, en su computador,
con su Excel en español, y después lo manda. Todo lo que puede salir distinto
sale distinto: el separador del CSV, la codificación, la coma decimal, las
mayúsculas de los encabezados, las columnas en otro orden, una fila en blanco
en el medio.

Dos reglas que no son de estilo:

- **Nunca se confía en el orden de las columnas.** Se mapean por nombre de
  encabezado normalizado: minúsculas, sin acentos, sin espacios de sobra.
- **El tipo de archivo se valida por contenido**, no por la extensión del
  nombre, que la escribe quien sube el archivo y no dice nada de lo que hay
  adentro.
"""

import csv
import io
import unicodedata
import zipfile
from decimal import Decimal, InvalidOperation

import filetype
from openpyxl import load_workbook

#: Formatos de planilla que se rechazan con una explicación, en vez de un
#: «no se acepta» a secas. Son los dos que la gente manda por error.
FORMATOS_EXPLICADOS = {
    "application/vnd.ms-excel": (
        "El formato .xls es antiguo. Abre el archivo en Excel y usa "
        "Archivo → Guardar como → Libro de Excel (.xlsx)."
    ),
    "application/x-rar-compressed": (
        "El formato .rar no se acepta. Abre el archivo, selecciona las fotos y "
        "usa clic derecho → Comprimir en archivo ZIP."
    ),
}


class ArchivoInvalido(Exception):
    """El archivo no se puede leer. El mensaje se le muestra a la persona."""


def normalizar(texto: str) -> str:
    """
    Un encabezado como clave: minúsculas, sin acentos, sin espacios de sobra.

    «Precio Neto», «precio neto» y «PRECIO_NETO» son la misma columna. Quien
    llena la planilla no tiene por qué saber cuál esperábamos.
    """
    if texto is None:
        return ""

    sin_acentos = unicodedata.normalize("NFKD", str(texto))
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return sin_acentos.strip().lower().replace(" ", "_")


#: Los ocho bytes con que empiezan los archivos de Office anteriores a 2007:
#: .xls, .doc y .ppt. Se reconocen a mano porque `filetype` pide más contexto
#: del que tenemos, y son justo los que la gente manda por error.
FIRMA_OFFICE_ANTIGUO = bytes.fromhex("d0cf11e0a1b11ae1")


def tipo_real(archivo) -> str | None:
    """Qué es el archivo según sus primeros bytes, no según su nombre."""
    archivo.seek(0)
    cabecera = archivo.read(261)
    archivo.seek(0)

    if cabecera.startswith(FIRMA_OFFICE_ANTIGUO):
        return "application/vnd.ms-excel"

    reconocido = filetype.guess(cabecera)
    return reconocido.mime if reconocido else None


def es_xlsx(archivo) -> bool:
    """
    Si el archivo es un libro de Excel.

    No alcanza con mirar los primeros bytes: **un .xlsx es un .zip**, así que
    por fuera son idénticos y las bibliotecas que leen la firma devuelven
    `application/zip` para los dos. Lo que los distingue está adentro: un libro
    de Excel trae `xl/workbook.xml`.
    """
    if tipo_real(archivo) != "application/zip":
        return False

    archivo.seek(0)
    try:
        with zipfile.ZipFile(archivo) as comprimido:
            dentro = set(comprimido.namelist())
    except zipfile.BadZipFile:
        return False
    finally:
        archivo.seek(0)

    return "xl/workbook.xml" in dentro


def revisar_planilla(archivo) -> None:
    """
    Que el archivo sea una planilla de las que sabemos leer.

    Lanza `ArchivoInvalido` con un mensaje que se le puede mostrar a la persona.
    """
    mime = tipo_real(archivo)

    if mime in FORMATOS_EXPLICADOS:
        raise ArchivoInvalido(FORMATOS_EXPLICADOS[mime])

    if mime is None:
        # Sin firma reconocible: puede ser un CSV, que es texto plano. Si no se
        # deja leer como texto, el lector lo dirá.
        return

    if mime == "application/zip" and not es_xlsx(archivo):
        raise ArchivoInvalido(
            "Este archivo es un .zip, no una planilla. El .zip es para las fotos."
        )

    if mime == "application/zip":
        return  # Es un .xlsx.

    raise ArchivoInvalido("Este archivo no es una planilla. Se aceptan .xlsx y .csv.")


def leer(archivo) -> list[dict]:
    """
    Las filas de la planilla, cada una como un diccionario por encabezado.

    Devuelve además el número de fila tal como lo ve la persona en Excel —con
    el encabezado contando como la 1—, porque el resumen de errores tiene que
    decirle dónde mirar.
    """
    revisar_planilla(archivo)

    if es_xlsx(archivo):
        return _leer_xlsx(archivo)
    return _leer_csv(archivo)


def _leer_xlsx(archivo) -> list[dict]:
    archivo.seek(0)
    try:
        libro = load_workbook(archivo, read_only=True, data_only=True)
    except Exception as error:  # noqa: BLE001 — openpyxl lanza de todo
        raise ArchivoInvalido("No pudimos abrir la planilla.") from error

    hoja = libro[libro.sheetnames[0]]
    filas = hoja.iter_rows(values_only=True)

    try:
        encabezados = [normalizar(c) for c in next(filas)]
    except StopIteration:
        raise ArchivoInvalido("La planilla está vacía.") from None

    leidas = []
    for numero, valores in enumerate(filas, start=2):
        if all(v is None or str(v).strip() == "" for v in valores):
            continue  # Fila en blanco: en Excel sobran al final.
        leidas.append({"_fila": numero, **_emparejar(encabezados, valores)})

    libro.close()
    return leidas


def _leer_csv(archivo) -> list[dict]:
    texto = _decodificar(archivo)

    try:
        dialecto = csv.Sniffer().sniff(texto[:4096], delimiters=";,")
        separador = dialecto.delimiter
    except csv.Error:
        # Excel en español exporta con punto y coma, así que es la apuesta
        # razonable cuando no se puede deducir.
        separador = ";"

    lector = csv.reader(io.StringIO(texto), delimiter=separador)

    try:
        encabezados = [normalizar(c) for c in next(lector)]
    except StopIteration:
        raise ArchivoInvalido("El archivo está vacío.") from None

    leidas = []
    for numero, valores in enumerate(lector, start=2):
        if not any(v.strip() for v in valores):
            continue
        leidas.append({"_fila": numero, **_emparejar(encabezados, valores)})

    return leidas


def _decodificar(archivo) -> str:
    """
    El texto del CSV, probando las dos codificaciones que llegan de verdad.

    UTF-8 es lo esperable; Windows-1252 es lo que escribe Excel en español si
    no se elige otra cosa, y es donde se rompen las tildes y las eñes.
    """
    archivo.seek(0)
    crudo = archivo.read()
    archivo.seek(0)

    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            return crudo.decode(codificacion)
        except UnicodeDecodeError:
            continue

    raise ArchivoInvalido(
        "No pudimos leer el archivo. Guárdalo como CSV UTF-8 o como .xlsx."
    )


def _emparejar(encabezados: list[str], valores) -> dict:
    """
    Cada valor bajo su encabezado.

    Las columnas de más se ignoran y las de menos quedan vacías: una planilla
    con una columna extra no tiene por qué fallar.
    """
    fila = {}
    for indice, encabezado in enumerate(encabezados):
        if not encabezado:
            continue
        valor = valores[indice] if indice < len(valores) else None
        fila[encabezado] = "" if valor is None else str(valor).strip()
    return fila


# ── Leer un valor de una celda ──────────────────────────────────────────────


def texto(fila: dict, columna: str) -> str:
    return fila.get(columna, "").strip()


def entero(fila: dict, columna: str) -> int | None:
    """Un entero, o None si la celda está vacía. Lanza si tiene basura."""
    crudo = texto(fila, columna)
    if not crudo:
        return None

    # Excel a veces entrega «4990.0» aunque la celda se vea «4990».
    try:
        return int(Decimal(crudo.replace(".", "").replace(",", ".")))
    except (InvalidOperation, ValueError):
        raise ValorInvalido(columna, crudo) from None


def decimal(fila: dict, columna: str) -> Decimal | None:
    """
    Un decimal, aceptando la coma como separador.

    «1,5» y «1.5» son lo mismo: en Chile se escribe con coma y Excel en español
    la exporta así.
    """
    crudo = texto(fila, columna)
    if not crudo:
        return None

    try:
        return Decimal(crudo.replace(",", "."))
    except InvalidOperation:
        raise ValorInvalido(columna, crudo) from None


#: Lo que se acepta como «sí» en una columna de sí/no.
AFIRMATIVOS = {"si", "sí", "s", "true", "verdadero", "1", "x"}
NEGATIVOS = {"no", "n", "false", "falso", "0", ""}


def booleano(fila: dict, columna: str, por_omision: bool) -> bool:
    """
    Sí o no, en las formas en que la gente lo escribe de verdad.

    Una celda vacía toma el valor por omisión; una con cualquier otra cosa
    falla, porque adivinar acá cambia si el producto lleva inventario.
    """
    crudo = normalizar(texto(fila, columna))
    if crudo == "":
        return por_omision
    if crudo in AFIRMATIVOS:
        return True
    if crudo in NEGATIVOS:
        return False

    raise ValorInvalido(columna, crudo)


class ValorInvalido(Exception):
    """Una celda que no se pudo leer. Sabe decir cuál y qué traía."""

    def __init__(self, columna: str, valor: str):
        self.columna = columna
        self.valor = valor
        super().__init__(f"«{valor}» no sirve en la columna {columna}.")


def exigir_columnas(filas: list[dict], obligatorias: list[str]) -> None:
    """
    Que la planilla sea la que creíamos.

    Sin esto, un archivo que no es una planilla —o la planilla equivocada— se
    lee como cero filas y devuelve un resumen vacío: «0 nuevos, 0 rechazados».
    Eso se parece demasiado a que funcionó.
    """
    if not filas:
        raise ArchivoInvalido(
            "La planilla no tiene filas. Revisa que los datos estén en la "
            "primera hoja."
        )

    presentes = set(filas[0]) - {"_fila"}
    faltan = [c for c in obligatorias if c not in presentes]

    if faltan:
        raise ArchivoInvalido(
            "A la planilla le faltan columnas: "
            + ", ".join(faltan)
            + ". Descarga la plantilla y copia tus datos ahí."
        )
