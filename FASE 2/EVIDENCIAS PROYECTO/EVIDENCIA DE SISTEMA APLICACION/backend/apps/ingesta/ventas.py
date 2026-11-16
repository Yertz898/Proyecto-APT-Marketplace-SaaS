"""
Las ventas que la tienda hizo antes de llegar a la plataforma.

Sin historia, una tienda nueva abre el panel de ventas en cero y el pronóstico
le dice que no tiene meses suficientes. Esta carga deja esas ventas como
pedidos entregados, con su fecha real, para que el panel, el pronóstico y los
segmentos partan con datos.

Misma forma que las otras cargas: `revisar` dice qué pasaría y `aplicar`
escribe. Dos cosas propias de esta:

- **No toca el inventario.** Son ventas que ya ocurrieron; el stock de hoy es
  el que la tienda cargó en su catálogo.
- **Se agrupan en pedidos.** Las filas con el mismo valor en la columna
  `pedido` van juntas; si esa columna viene vacía, se agrupan por fecha y
  cliente, que es como se ve una compra en un libro de ventas.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.catalogo.models import Producto
from apps.ingesta.planillas import ValorInvalido, decimal, exigir_columnas, texto
from apps.pedidos.models import LineaPedido, Pedido
from apps.precios.dinero import desglose

COLUMNAS = ["fecha", "codigo_producto", "cantidad", "precio_unitario_neto", "cliente"]
OPCIONALES = ["pedido"]

#: Prefijo del folio de lo que entra por esta carga, para distinguirlo de los
#: pedidos hechos en la vitrina.
PREFIJO = "HIS-"
NOTA = "Venta anterior, cargada desde planilla."


class FilaInvalida(Exception):
    """La fila no sirve. El mensaje se le muestra a la persona."""


@dataclass
class ResumenVentas:
    crear: int = 0
    actualizar: int = 0
    rechazos: list[dict] = field(default_factory=list)
    #: Las líneas listas, agrupadas por pedido.
    pedidos: dict[str, list[dict]] = field(default_factory=dict)

    @property
    def rechazar(self) -> int:
        return len(self.rechazos)


def revisar(tienda, filas: list[dict]) -> ResumenVentas:
    """Qué pedidos se crearían. No escribe nada."""
    exigir_columnas(filas, COLUMNAS)

    resumen = ResumenVentas()
    productos = {p.codigo: p for p in Producto.objects.de_tienda(tienda)}
    ya_cargadas = _lineas_ya_cargadas(tienda)
    hoy = timezone.localdate()

    for fila in filas:
        numero = fila["_fila"]
        try:
            datos = _convertir(fila, productos, hoy)
        except (ValorInvalido, FilaInvalida) as error:
            resumen.rechazos.append({"fila": numero, "motivo": str(error)})
            continue

        huella = (
            datos["fecha"],
            datos["producto"].pk,
            datos["cantidad"],
            datos["cliente"],
        )
        if huella in ya_cargadas:
            resumen.rechazos.append(
                {"fila": numero, "motivo": "Esta venta ya está cargada."}
            )
            continue
        ya_cargadas.add(huella)

        grupo = datos["pedido"] or f"{datos['fecha']}|{datos['cliente'].lower()}"
        resumen.pedidos.setdefault(grupo, []).append(datos)

    resumen.crear = len(resumen.pedidos)
    return resumen


@transaction.atomic
def aplicar(tienda, resumen: ResumenVentas) -> tuple[int, int]:
    """Crea los pedidos entregados. Devuelve (creados, 0)."""
    zona = timezone.get_current_timezone()

    for lineas in resumen.pedidos.values():
        neto_total = sum(linea["subtotal"] for linea in lineas)
        cifras = desglose(neto_total)
        primera = lineas[0]

        pedido = Pedido.objects.create(
            tienda=tienda,
            folio=f"{PREFIJO}{uuid.uuid4().hex[:8].upper()}",
            nombre_contacto=primera["cliente"],
            telefono_contacto="",
            notas=NOTA,
            estado=Pedido.Estado.ENTREGADO,
            total_neto=cifras["neto"],
            total_iva=cifras["iva"],
            total=cifras["total"],
        )
        for linea in lineas:
            partes = desglose(linea["subtotal"])
            LineaPedido.objects.create(
                pedido=pedido,
                producto=linea["producto"],
                cantidad=linea["cantidad"],
                precio_unitario_neto=linea["precio"],
                subtotal_neto=partes["neto"],
                subtotal_iva=partes["iva"],
                subtotal_total=partes["total"],
            )

        # La fecha de creación se fija sola al crear; para que la venta quede
        # en su mes real hay que corregirla después, con un update directo.
        momento = timezone.make_aware(
            datetime.combine(primera["fecha"], datetime.min.time()).replace(hour=12),
            zona,
        )
        Pedido.objects.filter(pk=pedido.pk).update(fecha_creacion=momento)

    return len(resumen.pedidos), 0


def _lineas_ya_cargadas(tienda) -> set[tuple]:
    """Lo que ya entró por esta carga, para no duplicarlo si suben el mismo archivo."""
    lineas = LineaPedido.objects.filter(
        pedido__tienda=tienda, pedido__folio__startswith=PREFIJO
    ).values_list(
        "pedido__fecha_creacion", "producto_id", "cantidad", "pedido__nombre_contacto"
    )
    return {
        (timezone.localtime(fecha).date(), producto, cantidad, cliente)
        for fecha, producto, cantidad, cliente in lineas
    }


def _fecha(crudo: str) -> date:
    """dd-mm-aaaa, dd/mm/aaaa, aaaa-mm-dd, o la fecha que entrega Excel."""
    crudo = crudo.strip().split(" ")[0]
    for formato in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(crudo, formato).date()
        except ValueError:
            continue
    raise ValorInvalido("fecha", crudo)


def _convertir(fila: dict, productos: dict, hoy: date) -> dict:
    crudo_fecha = texto(fila, "fecha")
    if not crudo_fecha:
        raise FilaInvalida("Falta la fecha.")
    fecha = _fecha(crudo_fecha)
    if fecha > hoy:
        raise FilaInvalida(
            "La fecha está en el futuro: aquí van ventas que ya ocurrieron."
        )

    codigo = texto(fila, "codigo_producto")
    if not codigo:
        raise FilaInvalida("Falta el código del producto.")
    producto = productos.get(codigo)
    if producto is None:
        raise FilaInvalida(
            f"No tienes ningún producto con el código {codigo}. "
            "Carga primero el catálogo."
        )

    cantidad = decimal(fila, "cantidad")
    if cantidad is None or cantidad <= 0:
        raise FilaInvalida("La cantidad tiene que ser mayor que cero.")

    precio = decimal(fila, "precio_unitario_neto")
    if precio is None or precio < 0:
        raise FilaInvalida("Falta el precio unitario neto.")

    cliente = texto(fila, "cliente")
    if not cliente:
        raise FilaInvalida("Falta el nombre del cliente.")

    subtotal = int((cantidad * precio).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    return {
        "fecha": fecha,
        "producto": producto,
        "cantidad": cantidad.quantize(Decimal("0.01")),
        "precio": precio.quantize(Decimal("0.01")),
        "subtotal": subtotal,
        "cliente": cliente[:150],
        "pedido": texto(fila, "pedido")[:60],
    }
