"""
Qué hacer con cada fila de una planilla de tramos de precio.

Misma forma que la de productos: `revisar` dice qué pasaría y `aplicar`
escribe. La clave acá es `(producto, unidad del umbral, umbral)`, porque dos
tramos con el mismo umbral y la misma unidad se pisan y el motor no sabría cuál
aplicar.
"""

from dataclasses import dataclass, field

from django.db import transaction

from apps.catalogo.models import Producto
from apps.ingesta.planillas import (
    ValorInvalido,
    decimal,
    entero,
    exigir_columnas,
    normalizar,
    texto,
)
from apps.precios.models import TramoPrecio, UnidadUmbral

COLUMNAS = ["codigo_producto", "umbral", "unidad_umbral", "precio_neto"]


@dataclass
class ResumenTramos:
    crear: int = 0
    actualizar: int = 0
    rechazos: list[dict] = field(default_factory=list)
    listas: list[dict] = field(default_factory=list)

    @property
    def rechazar(self) -> int:
        return len(self.rechazos)


def revisar(tienda, filas: list[dict]) -> ResumenTramos:
    """Qué pasaría con cada tramo. No escribe nada."""
    exigir_columnas(filas, COLUMNAS)

    resumen = ResumenTramos()

    productos = {p.codigo: p for p in Producto.objects.de_tienda(tienda)}
    existentes = {
        (t.producto_id, t.unidad_umbral, t.umbral)
        for t in TramoPrecio.objects.de_tienda(tienda)
    }
    vistos: set[tuple] = set()

    for fila in filas:
        numero = fila["_fila"]
        try:
            datos = _convertir(fila, productos)
        except (ValorInvalido, FilaInvalida) as error:
            resumen.rechazos.append({"fila": numero, "motivo": str(error)})
            continue

        clave = (datos["producto"].pk, datos["unidad_umbral"], datos["umbral"])

        if clave in vistos:
            resumen.rechazos.append(
                {
                    "fila": numero,
                    "motivo": "Este tramo aparece dos veces en la planilla.",
                }
            )
            continue

        vistos.add(clave)
        resumen.listas.append(datos)

        if clave in existentes:
            resumen.actualizar += 1
        else:
            resumen.crear += 1

    return resumen


@transaction.atomic
def aplicar(tienda, resumen: ResumenTramos) -> tuple[int, int]:
    """Escribe los tramos. Devuelve (creados, actualizados)."""
    creados = actualizados = 0

    for datos in resumen.listas:
        _, creado = TramoPrecio.objects.update_or_create(
            tienda=tienda,
            producto=datos["producto"],
            unidad_umbral=datos["unidad_umbral"],
            umbral=datos["umbral"],
            defaults={"valor": datos["valor"]},
        )
        if creado:
            creados += 1
        else:
            actualizados += 1

    return creados, actualizados


class FilaInvalida(Exception):
    """La fila no sirve. El mensaje se le muestra a la persona."""


def _convertir(fila: dict, productos: dict) -> dict:
    codigo = texto(fila, "codigo_producto")
    if not codigo:
        raise FilaInvalida("Falta el código del producto.")

    producto = productos.get(codigo)
    if producto is None:
        raise FilaInvalida(
            f"No tienes ningún producto con el código {codigo}. "
            "Carga primero el catálogo."
        )

    umbral = decimal(fila, "umbral")
    if umbral is None or umbral < 0:
        raise FilaInvalida("El umbral tiene que ser un número de 0 para arriba.")

    valor = entero(fila, "precio_neto")
    if valor is None or valor <= 0:
        raise FilaInvalida("El precio tiene que ser mayor que 0.")

    return {
        "producto": producto,
        "unidad_umbral": _unidad(fila),
        "umbral": umbral,
        "valor": valor,
    }


def _unidad(fila: dict) -> str:
    crudo = normalizar(texto(fila, "unidad_umbral"))
    if not crudo:
        raise FilaInvalida("Falta la unidad del umbral: cantidad, monto o peso.")

    for valor, nombre in UnidadUmbral.choices:
        if crudo in (normalizar(valor), normalizar(nombre)):
            return valor

    aceptados = ", ".join(v for v, _ in UnidadUmbral.choices)
    raise FilaInvalida(
        f"«{texto(fila, 'unidad_umbral')}» no sirve como unidad. "
        f"Se acepta: {aceptados}."
    )
