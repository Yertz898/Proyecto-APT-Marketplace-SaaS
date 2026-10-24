"""
Las fotos del catálogo, en un .zip.

Un archivo comprimido que sube un desconocido es de lo más peligroso que
acepta un sistema, así que acá se desconfía de todo:

- **Las rutas internas se ignoran.** Una entrada llamada `../../etc/passwd` o
  `C:\\Windows\\algo` es un intento de escribir fuera de donde corresponde; de
  cada entrada se toma solo el nombre del archivo y nada más.
- **El tamaño descomprimido tiene tope**, además del comprimido. Un .zip de dos
  megas puede descomprimirse en varios gigas y llenar el disco; eso tiene
  nombre propio, «zip bomb».
- **Hay tope de cantidad de archivos**, por lo mismo.
- **Cada imagen se valida por contenido**, no por su extensión.
- **El nombre con que se guarda lo pone el sistema.** El del archivo solo sirve
  para emparejar con el producto.

El emparejado es por el nombre del archivo —sin extensión— contra el código del
producto, que es como la gente las nombra cuando las saca del teléfono.
"""

import zipfile
from dataclasses import dataclass, field
from pathlib import PurePath, PureWindowsPath

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction

from apps.catalogo.models import Producto
from apps.core.validadores import validar_imagen
from apps.ingesta.planillas import (
    ArchivoInvalido,
    es_xlsx,
    normalizar,
    tipo_real,
)

#: Cuántas imágenes puede traer un .zip.
MAXIMO_ARCHIVOS = 500

#: Cuánto puede pesar el .zip ya descomprimido, sumando todo.
MAXIMO_DESCOMPRIMIDO = 200 * 1024 * 1024


@dataclass
class ResumenFotos:
    emparejadas: int = 0
    productos_sin_foto: list[str] = field(default_factory=list)
    fotos_sin_producto: list[str] = field(default_factory=list)
    rechazos: list[dict] = field(default_factory=list)
    #: (producto, nombre dentro del zip) de lo que sí se va a guardar.
    listas: list[tuple] = field(default_factory=list)


def revisar(tienda, archivo) -> ResumenFotos:
    """Qué foto va a cada producto. No escribe nada."""
    if tipo_real(archivo) != "application/zip":
        raise ArchivoInvalido("Este archivo no es un .zip.")

    # Un .xlsx también es un .zip por dentro, así que hay que descartarlo
    # explícitamente o se aceptaría una planilla como si fueran fotos.
    if es_xlsx(archivo):
        raise ArchivoInvalido("Esto es una planilla, no un .zip de fotos.")

    resumen = ResumenFotos()
    productos = {
        normalizar(p.codigo): p for p in Producto.objects.de_tienda(tienda)
    }
    con_foto: set[str] = set()

    archivo.seek(0)
    try:
        comprimido = zipfile.ZipFile(archivo)
    except zipfile.BadZipFile as error:
        raise ArchivoInvalido("El .zip está dañado y no se puede abrir.") from error

    with comprimido:
        entradas = [e for e in comprimido.infolist() if not e.is_dir()]
        _revisar_limites(entradas)

        for entrada in entradas:
            nombre = _nombre_seguro(entrada.filename)
            if nombre is None:
                continue  # Entrada sin nombre utilizable; no es una foto.

            codigo = normalizar(PurePath(nombre).stem)
            producto = productos.get(codigo)

            if producto is None:
                resumen.fotos_sin_producto.append(nombre)
                continue

            try:
                _revisar_imagen(comprimido, entrada)
            except ValidationError as error:
                resumen.rechazos.append(
                    {"fila": 0, "motivo": f"{nombre}: {error.messages[0]}"}
                )
                continue

            resumen.listas.append((producto, entrada.filename, nombre))
            con_foto.add(producto.codigo)
            resumen.emparejadas += 1

    resumen.productos_sin_foto = sorted(
        p.codigo for p in productos.values() if p.codigo not in con_foto and not p.foto
    )
    return resumen


@transaction.atomic
def aplicar(archivo, resumen: ResumenFotos) -> int:
    """
    Guarda las fotos. Devuelve cuántas quedaron.

    El nombre con que se guarda lo arma el sistema a partir del código del
    producto: el del archivo subido nunca llega al disco.
    """
    archivo.seek(0)
    guardadas = 0

    with zipfile.ZipFile(archivo) as comprimido:
        for producto, dentro_del_zip, nombre in resumen.listas:
            contenido = comprimido.read(dentro_del_zip)
            extension = PurePath(nombre).suffix.lower() or ".jpg"

            producto.foto.save(
                f"{producto.codigo}{extension}",
                ContentFile(contenido),
                save=True,
            )
            guardadas += 1

    return guardadas


def _revisar_limites(entradas) -> None:
    if len(entradas) > MAXIMO_ARCHIVOS:
        raise ArchivoInvalido(
            f"El .zip trae {len(entradas)} archivos y el máximo es {MAXIMO_ARCHIVOS}."
        )

    descomprimido = sum(e.file_size for e in entradas)
    if descomprimido > MAXIMO_DESCOMPRIMIDO:
        megas = MAXIMO_DESCOMPRIMIDO // (1024 * 1024)
        raise ArchivoInvalido(
            f"Las fotos suman más de {megas} MB descomprimidas. Súbelas en tandas."
        )


def _nombre_seguro(dentro_del_zip: str) -> str | None:
    """
    Solo el nombre del archivo, sin nada de la ruta que venía adentro.

    `../../paso/algo.jpg` y `C:\\Users\\algo.jpg` se quedan en `algo.jpg`. No se
    rechaza la entrada: se le quita el poder de apuntar a otra parte.
    """
    # PureWindowsPath entiende las dos barras, así que sirve para un .zip hecho
    # en Windows y para uno hecho en Linux.
    nombre = PureWindowsPath(dentro_del_zip).name.strip()
    if not nombre or nombre.startswith("."):
        return None
    return nombre


def _revisar_imagen(comprimido, entrada) -> None:
    """Que la entrada sea de verdad una imagen de las que aceptamos."""
    contenido = comprimido.read(entrada)
    archivo = ContentFile(contenido, name=entrada.filename)
    archivo.size = len(contenido)
    validar_imagen(archivo)
