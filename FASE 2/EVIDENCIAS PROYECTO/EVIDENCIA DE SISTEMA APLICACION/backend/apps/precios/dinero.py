"""
El IVA y el redondeo, en un solo lugar.

La regla está en CONVENCIONES.md y se escribe acá una sola vez porque la van a
usar el catálogo, la cotización del granel y el pedido. Repetirla es la forma
segura de que tres pantallas muestren tres totales distintos.

    neto  = truncar(cantidad × precio unitario)
    iva   = neto × 0,19, redondeado medio hacia arriba
    total = neto + iva

El `round()` de Python redondea al par más cercano: con 3.828,50 devuelve 3.828
en vez de 3.829 y el total queda un peso corto. Por eso acá va `Decimal` con
`ROUND_HALF_UP` y nunca `float`.
"""

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

#: Impuesto al valor agregado en Chile.
TASA_IVA = Decimal("0.19")


def neto_de(cantidad: Decimal | int, precio_unitario: int) -> int:
    """
    Precio neto de una cantidad, truncado al peso.

    Se trunca y no se redondea a propósito: el neto es la base imponible y
    redondearla hacia arriba cobraría de más antes de aplicar el impuesto.
    """
    bruto = Decimal(cantidad) * Decimal(precio_unitario)
    return int(bruto.quantize(Decimal("1"), rounding=ROUND_DOWN))


def iva_de(neto: int) -> int:
    """IVA de un neto, redondeado medio hacia arriba."""
    return int(
        (Decimal(neto) * TASA_IVA).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


def desglose(neto: int) -> dict[str, int]:
    """Neto, IVA y total: lo que el pedido muestra por separado."""
    iva = iva_de(neto)
    return {"neto": neto, "iva": iva, "total": neto + iva}
