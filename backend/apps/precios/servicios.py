"""
Qué precio corresponde a una cantidad, en un solo lugar.

Lo usan la cotización de la vitrina, el carrito y el pedido. Si esto viviera en
tres partes, tres pantallas mostrarían tres totales distintos y el error
aparecería el día de la demostración.

La regla está en CONVENCIONES.md > Tramos de precio:

1. Los umbrales en `peso` o en `cantidad` tienen prioridad. Se toma el mayor
   que la cantidad pedida alcance.
2. Si no alcanza ninguno, se arma un **monto de referencia** —la cantidad por
   el `precio_neto` del producto— y se aplica el tramo por `monto` que ese
   monto alcance.
3. Si no llega ni al primer tramo por monto, se rechaza.
4. Si no hay tramos, se cobra el `precio_neto` del producto.

Los umbrales son **inclusivos**: «sobre 20 mil» incluye los $20.000 exactos.
"""

from dataclasses import dataclass
from decimal import Decimal

from apps.precios.dinero import desglose, neto_de
from apps.precios.models import UnidadUmbral


class MotivoRechazo:
    """
    Por qué no se puede cotizar. Son dos cosas distintas y se confunden fácil.

    - `bajo_minimo_por_monto`: lo pedido no alcanza el umbral del primer tramo
      por monto. De acá salen los $20.000 de compra mínima del cliente piloto.
    - `bajo_cantidad_minima`: se pidió menos que la `cantidad_minima` del
      producto, que es otra cosa y tiene otro mensaje.
    """

    BAJO_MINIMO_POR_MONTO = "bajo_minimo_por_monto"
    BAJO_CANTIDAD_MINIMA = "bajo_cantidad_minima"
    SIN_STOCK = "sin_stock"


@dataclass(frozen=True)
class Cotizacion:
    """
    Lo que cuesta una cantidad de un producto.

    `rechazo` y el resto son excluyentes: si hay rechazo, no hay precio. Se
    devuelve en vez de lanzarse porque la vitrina necesita mostrar el motivo,
    no un error.
    """

    cantidad: Decimal
    precio_unitario: int = 0
    neto: int = 0
    iva: int = 0
    total: int = 0
    #: Umbral del tramo aplicado, o None si se cobró el precio base.
    tramo_aplicado: Decimal | None = None
    unidad_tramo: str | None = None
    #: "Llevando N más, el precio baja a X". Se avisa, no se cambia la cantidad.
    aviso: str | None = None
    rechazo: str | None = None
    motivo: str | None = None

    @property
    def aceptada(self) -> bool:
        return self.rechazo is None


def cotizar(producto, cantidad: Decimal) -> Cotizacion:
    """Qué cuesta llevar esta cantidad de este producto."""
    cantidad = Decimal(cantidad)

    if cantidad < producto.cantidad_minima:
        return _rechazo(
            cantidad,
            f"La compra mínima de este producto es "
            f"{_cantidad_legible(producto, producto.cantidad_minima)}.",
            MotivoRechazo.BAJO_CANTIDAD_MINIMA,
        )

    if producto.controla_stock and cantidad > (producto.stock or 0):
        disponible = _cantidad_legible(producto, producto.stock or Decimal(0))
        return _rechazo(
            cantidad,
            f"Quedan {disponible} de este producto.",
            MotivoRechazo.SIN_STOCK,
        )

    tramos = list(producto.tramos.all())
    tramo = _tramo_por_cantidad(tramos, producto, cantidad)

    if tramo is None:
        tramo, rechazo = _tramo_por_monto(tramos, producto, cantidad)
        if rechazo is not None:
            return rechazo

    precio_unitario = tramo.valor if tramo else producto.precio_neto
    neto = neto_de(cantidad, precio_unitario)
    cifras = desglose(neto)

    return Cotizacion(
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        neto=cifras["neto"],
        iva=cifras["iva"],
        total=cifras["total"],
        tramo_aplicado=tramo.umbral if tramo else None,
        unidad_tramo=tramo.unidad_umbral if tramo else None,
        aviso=_aviso_de_conveniencia(tramos, producto, cantidad, neto),
    )


# ── Cómo se elige el tramo ──────────────────────────────────────────────────


def _unidad_natural(producto) -> str:
    """En qué se miden los umbrales directos de este producto."""
    from apps.catalogo.models import FormaVenta

    if producto.forma_venta == FormaVenta.PESO:
        return UnidadUmbral.PESO
    return UnidadUmbral.CANTIDAD


def _tramo_por_cantidad(tramos, producto, cantidad):
    """
    El mayor tramo en peso o en cantidad que la cantidad alcanza.

    Tienen prioridad sobre los de monto: son la forma directa de decir «desde
    medio kilo, este precio», sin pasar por el valor de la compra.
    """
    unidad = _unidad_natural(producto)
    alcanzados = [
        t for t in tramos if t.unidad_umbral == unidad and cantidad >= t.umbral
    ]
    return max(alcanzados, key=lambda t: t.umbral, default=None)


def _tramo_por_monto(tramos, producto, cantidad):
    """
    El tramo por monto que alcanza el monto de referencia.

    El monto de referencia se calcula con el `precio_neto` del producto, que es
    su precio base. Devuelve (tramo, rechazo): si hay tramos por monto y el
    monto no llega ni al primero, la compra se rechaza.
    """
    por_monto = [t for t in tramos if t.unidad_umbral == UnidadUmbral.MONTO]
    if not por_monto:
        return None, None

    referencia = neto_de(cantidad, producto.precio_neto)
    alcanzados = [t for t in por_monto if referencia >= t.umbral]

    if not alcanzados:
        minimo = min(t.umbral for t in por_monto)
        return None, _rechazo(
            cantidad,
            f"La compra mínima es de {_pesos(minimo)}.",
            MotivoRechazo.BAJO_MINIMO_POR_MONTO,
        )

    return max(alcanzados, key=lambda t: t.umbral), None


def _aviso_de_conveniencia(tramos, producto, cantidad, neto) -> str | None:
    """
    Cuando llevar más sale más barato que lo pedido.

    Pasa de verdad: en el cliente piloto, entre 893 y 999 gramos de la línea
    hombre cuesta más que un kilo entero. Se avisa y no se cambia la cantidad
    por el comprador.
    """
    unidad = _unidad_natural(producto)
    mayores = [
        t for t in tramos if t.unidad_umbral == unidad and t.umbral > cantidad
    ]
    if not mayores:
        return None

    siguiente = min(mayores, key=lambda t: t.umbral)
    neto_mayor = neto_de(siguiente.umbral, siguiente.valor)
    if neto_mayor >= neto:
        return None

    return (
        f"Llevando {_cantidad_legible(producto, siguiente.umbral)} pagas "
        f"{_pesos(neto_mayor)} neto, menos que ahora."
    )


# ── Texto ───────────────────────────────────────────────────────────────────


def _rechazo(cantidad, mensaje, motivo) -> Cotizacion:
    return Cotizacion(cantidad=cantidad, rechazo=mensaje, motivo=motivo)


def _pesos(monto) -> str:
    return f"${int(monto):,}".replace(",", ".")


def _cantidad_legible(producto, cantidad: Decimal) -> str:
    """
    La cantidad con su unidad, sin ceros decimales de adorno.

    Se arma desde los datos del producto: la plataforma no sabe si lo que
    cuenta son gramos, piezas o lotes, y no debe saberlo.
    """
    from apps.catalogo.models import UnidadMedida

    if cantidad == cantidad.to_integral_value():
        numero = f"{int(cantidad)}"
    else:
        numero = f"{cantidad.normalize()}".replace(".", ",")

    if producto.unidad_medida == UnidadMedida.UNIDAD:
        return numero
    return f"{numero} {producto.unidad_medida}"
