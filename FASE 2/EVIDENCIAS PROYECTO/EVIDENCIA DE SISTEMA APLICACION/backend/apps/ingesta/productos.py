"""
Qué hacer con cada fila de una planilla de productos.

Se parte en dos a propósito: `revisar` dice qué va a pasar y **no escribe
nada**; `aplicar` escribe. Entre las dos pasa la decisión del dueño, que ve el
resumen antes de que nada toque su catálogo.

La clave es `(tienda, código)`: subir dos veces la misma planilla no duplica.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalogo.models import (
    Categoria,
    FormaVenta,
    Producto,
    UnidadMedida,
)
from apps.ingesta.planillas import (
    ValorInvalido,
    booleano,
    decimal,
    entero,
    exigir_columnas,
    normalizar,
    texto,
)

#: Las columnas que la plantilla entrega, en orden.
COLUMNAS = [
    "codigo",
    "nombre",
    "descripcion",
    "categoria",
    "forma_venta",
    "unidad_medida",
    "precio_neto",
    "controla_stock",
    "stock",
    "cantidad_minima",
    "foto",
]

#: Sin estas dos no hay fila que valga.
OBLIGATORIAS = ["codigo", "nombre", "precio_neto"]


@dataclass
class Resumen:
    """Lo que va a pasar si se confirma. Ninguna de estas filas se escribió."""

    crear: int = 0
    actualizar: int = 0
    rechazos: list[dict] = field(default_factory=list)
    ausentes: list[str] = field(default_factory=list)
    #: Las filas que sí se pueden aplicar, ya convertidas.
    listas: list[dict] = field(default_factory=list)

    @property
    def rechazar(self) -> int:
        return len(self.rechazos)


def revisar(tienda, filas: list[dict]) -> Resumen:
    """
    Qué pasaría con cada fila. No escribe nada.

    Una fila mala no bota a las demás: se anota con su número y su motivo, y el
    resto sigue. El dueño decide con el resumen a la vista.
    """
    exigir_columnas(filas, OBLIGATORIAS)

    resumen = Resumen()

    existentes = set(
        Producto.objects.de_tienda(tienda).values_list("codigo", flat=True)
    )
    categorias = {
        normalizar(c.nombre): c for c in Categoria.objects.de_tienda(tienda)
    }
    vistos: set[str] = set()

    for fila in filas:
        numero = fila["_fila"]
        try:
            datos = _convertir(fila, categorias)
        except ValorInvalido as error:
            resumen.rechazos.append({"fila": numero, "motivo": str(error)})
            continue
        except FilaInvalida as error:
            resumen.rechazos.append({"fila": numero, "motivo": str(error)})
            continue

        codigo = datos["codigo"]

        if codigo in vistos:
            resumen.rechazos.append(
                {
                    "fila": numero,
                    "motivo": f"El código {codigo} aparece dos veces en la planilla.",
                }
            )
            continue

        # Las reglas cruzadas del modelo, antes de prometer que se puede. Si no
        # se miran acá, el error aparece recién al confirmar, con la mitad
        # aplicada.
        try:
            _ensayar(tienda, datos)
        except ValidationError as error:
            resumen.rechazos.append(
                {"fila": numero, "motivo": _primer_motivo(error)}
            )
            continue

        vistos.add(codigo)
        resumen.listas.append({"_fila": numero, **datos})

        if codigo in existentes:
            resumen.actualizar += 1
        else:
            resumen.crear += 1

    resumen.ausentes = sorted(existentes - vistos)
    return resumen


@transaction.atomic
def aplicar(tienda, resumen: Resumen, desactivar_ausentes: bool) -> tuple[int, int]:
    """
    Escribe lo que el resumen dijo que se podía. Devuelve (creadas, actualizadas).

    Va en una transacción: o entra la planilla entera o no entra nada. A medio
    aplicar, el dueño no sabría qué quedó.
    """
    creadas = actualizadas = 0

    for fila in resumen.listas:
        datos = {k: v for k, v in fila.items() if k != "_fila"}
        codigo = datos.pop("codigo")

        _, creado = Producto.objects.update_or_create(
            tienda=tienda, codigo=codigo, defaults=datos
        )
        if creado:
            creadas += 1
        else:
            actualizadas += 1

    if desactivar_ausentes and resumen.ausentes:
        # Desactivar y no borrar: una planilla incompleta no puede vaciar una
        # tienda, y lo desactivado conserva su historial.
        Producto.objects.de_tienda(tienda).filter(
            codigo__in=resumen.ausentes
        ).update(activo=False)

    return creadas, actualizadas


# ── De una fila de texto a los campos del modelo ────────────────────────────


class FilaInvalida(Exception):
    """La fila no sirve. El mensaje se le muestra a la persona."""


def _convertir(fila: dict, categorias: dict) -> dict:
    for columna in OBLIGATORIAS:
        if not texto(fila, columna):
            raise FilaInvalida(f"Falta {columna.replace('_', ' ')}.")

    forma = _opcion(fila, "forma_venta", FormaVenta, FormaVenta.UNIDAD)
    unidad = _opcion(
        fila,
        "unidad_medida",
        UnidadMedida,
        UnidadMedida.GRAMO if forma == FormaVenta.PESO else UnidadMedida.UNIDAD,
    )

    controla = booleano(fila, "controla_stock", por_omision=True)
    stock = decimal(fila, "stock")

    if controla and stock is None:
        # Que la columna venga vacía es lo normal en una planilla nueva: se
        # entiende como «todavía no tengo», no como un error.
        stock = Decimal("0")
    if not controla:
        stock = None

    datos = {
        "codigo": texto(fila, "codigo"),
        "nombre": texto(fila, "nombre"),
        "descripcion": texto(fila, "descripcion"),
        "categoria": _categoria(fila, categorias),
        "forma_venta": forma,
        "unidad_medida": unidad,
        "precio_neto": entero(fila, "precio_neto"),
        "controla_stock": controla,
        "stock": stock,
        "activo": True,
    }

    minima = decimal(fila, "cantidad_minima")
    if minima is not None:
        datos["cantidad_minima"] = minima

    if datos["precio_neto"] is None or datos["precio_neto"] <= 0:
        raise FilaInvalida("El precio tiene que ser mayor que 0.")

    return datos


def _opcion(fila: dict, columna: str, opciones, por_omision: str) -> str:
    """
    Un valor de lista cerrada, tolerante con cómo se escribe.

    Acepta tanto el valor («peso») como su nombre visible («Por peso»), porque
    la plantilla muestra uno y la gente escribe el otro.
    """
    crudo = normalizar(texto(fila, columna))
    if not crudo:
        return por_omision

    for valor, nombre in opciones.choices:
        if crudo in (normalizar(valor), normalizar(nombre)):
            return valor

    aceptados = ", ".join(v for v, _ in opciones.choices)
    raise FilaInvalida(
        f"«{texto(fila, columna)}» no sirve en {columna.replace('_', ' ')}. "
        f"Se acepta: {aceptados}."
    )


def _categoria(fila: dict, categorias: dict):
    """
    La categoría, buscada dentro de la tienda. No se crea sola.

    Crear categorías desde la planilla llenaría el catálogo de variantes mal
    escritas de la misma palabra.
    """
    nombre = texto(fila, "categoria")
    if not nombre:
        return None

    categoria = categorias.get(normalizar(nombre))
    if categoria is None:
        raise FilaInvalida(
            f"La categoría «{nombre}» no existe en tu tienda. Créala antes de cargar."
        )
    return categoria


def _ensayar(tienda, datos: dict) -> None:
    """Las validaciones del modelo, sobre un producto que no se guarda."""
    campos = {k: v for k, v in datos.items() if k != "codigo"}
    Producto(tienda=tienda, codigo=datos["codigo"], **campos).clean()


def _primer_motivo(error: ValidationError) -> str:
    """
    El primer mensaje del modelo, que es el que orienta.

    Mostrar los cinco de una fila es ruido: se corrige el primero y los demás
    suelen irse solos.
    """
    if hasattr(error, "error_dict"):
        for errores in error.error_dict.values():
            if errores:
                return errores[0].message
    return error.messages[0] if error.messages else "La fila no es válida."
