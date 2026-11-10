"""
Carga el historial de ventas del cliente a la base.

    docker compose exec api python manage.py importar_historial \\
        "data/JOYAS YE verdadero.xlsx"

Sin esto no hay con qué entrenar nada: la plataforma es nueva y su único
historial real es la planilla que el dueño llevó a mano. Ver
`apps/analitica/historial.py` para cómo se lee ese archivo.

**Los nombres se seudonimizan.** El libro trae 1.821 nombres de personas que
no dieron permiso para que aparezcan en ningún lado, y el volcado de esta base
sí viaja a las evidencias del proyecto, que son públicas. Cada cliente entra
como «Cliente 0427», y la correspondencia se escribe junto al archivo
original, en `data/`, que está fuera del repositorio. Las métricas salen
idénticas: para agrupar por recencia, frecuencia y monto da lo mismo cómo se
llame la persona.
"""

import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.analitica import historial
from apps.catalogo.models import Producto
from apps.pedidos.models import LineaPedido, Pedido
from apps.precios.dinero import desglose
from apps.tiendas.models import Tienda

#: Dónde queda la correspondencia entre el nombre real y el seudónimo.
#: Junto al archivo original y fuera del repositorio, nunca en la base.
NOMBRE_DEL_MAPA = "clientes-seudonimizados.csv"


class Command(BaseCommand):
    help = "Carga el historial de ventas del cliente desde su planilla."

    def add_arguments(self, parser):
        parser.add_argument("archivo", help="Ruta al .xlsx del cliente.")
        parser.add_argument(
            "--tienda",
            default="joyas-ye",
            help="Slug de la tienda a la que pertenece el historial.",
        )
        parser.add_argument(
            "--limpiar",
            action="store_true",
            help="Borra el historial importado antes de cargar.",
        )
        parser.add_argument(
            "--desplazar-anos",
            type=int,
            default=0,
            dest="desplazar_anos",
            help=(
                "Adelanta el historial esta cantidad de AÑOS. En años enteros "
                "a propósito: cada venta conserva su mes y la estacionalidad "
                "del negocio no se corre."
            ),
        )
        parser.add_argument(
            "--ensayo",
            action="store_true",
            help="Lee el archivo y dice qué pasaría, sin escribir nada.",
        )

    def handle(self, *args, **opciones):
        ruta = Path(opciones["archivo"])
        if not ruta.exists():
            raise CommandError(f"No existe el archivo {ruta}.")

        try:
            tienda = Tienda.objects.get(slug=opciones["tienda"])
        except Tienda.DoesNotExist as error:
            raise CommandError(
                f"No existe la tienda «{opciones['tienda']}»."
            ) from error

        lectura = historial.leer(ruta)
        self.stdout.write(lectura.resumen())

        anos = opciones["desplazar_anos"]
        if anos:
            for venta in lectura.ventas:
                venta.fecha = _adelantar(venta.fecha, anos)
            self.stdout.write(
                self.style.WARNING(
                    f"Historial adelantado {anos} año(s): las fechas ya no son "
                    "las del libro del cliente. Queda anotado en cada pedido."
                )
            )
            self.anos_desplazados = anos

        productos = self._productos(tienda)
        aplicables, sin_producto = self._repartir(lectura.ventas, productos)

        self.stdout.write(
            f"se pueden cargar: {len(aplicables)}; "
            f"sin producto en el catálogo: {len(sin_producto)}"
        )

        if opciones["ensayo"]:
            self.stdout.write(self.style.WARNING("Ensayo: no se escribió nada."))
            return

        seudonimos = self._seudonimizar(aplicables, ruta)

        with transaction.atomic():
            if opciones["limpiar"]:
                # Por el prefijo y no por la nota entera: una corrida anterior
                # pudo haber usado otro desplazamiento.
                borrados = Pedido.objects.filter(
                    tienda=tienda, notas__startswith="Historial del cliente"
                ).delete()
                self.stdout.write(f"historial anterior borrado: {borrados}")

            creados = self._cargar(tienda, aplicables, productos, seudonimos)

        self.stdout.write(
            self.style.SUCCESS(f"{creados} pedidos cargados en {tienda}.")
        )
        self.stdout.write(
            f"correspondencia de nombres en {ruta.parent / NOMBRE_DEL_MAPA} "
            "(fuera del repositorio)."
        )

    # ── Pasos ───────────────────────────────────────────────────────────────

    #: Cuántos años se adelantó el historial, si se adelantó.
    anos_desplazados = 0

    def _marca(self) -> str:
        """
        Cómo se reconoce lo importado, y si sus fechas fueron movidas.

        Va en las notas del pedido y no en un campo nuevo: el historial es
        carga de datos y no una función del producto, así que no justifica una
        columna en una tabla que usan todas las tiendas. Que diga el
        desplazamiento importa: quien mire un pedido de 2026 tiene que poder
        enterarse de que esa venta ocurrió antes.
        """
        base = "Historial del cliente, importado."
        if self.anos_desplazados:
            return f"{base} Fecha adelantada {self.anos_desplazados} año(s)."
        return base

    def _productos(self, tienda) -> dict[str, Producto]:
        codigos = set(historial.PRODUCTO_POR_TRAMO.values())
        encontrados = {
            p.codigo: p
            for p in Producto.objects.de_tienda(tienda).filter(codigo__in=codigos)
        }
        faltan = codigos - set(encontrados)
        if faltan:
            raise CommandError(
                "Faltan productos en el catálogo de la tienda: "
                + ", ".join(sorted(faltan))
                + ". Corre primero «cargar_demo»."
            )
        return encontrados

    def _repartir(self, ventas, productos):
        """
        Separa lo que se puede cargar de lo que no.

        No se puede cargar lo que no se vendió por gramo: el libro empieza
        vendiendo piezas sueltas y lotes, y esos productos no existen en el
        catálogo de hoy. Son las ventas de los primeros meses, cuando el
        negocio todavía no vendía al peso.
        """
        aplicables, sin_producto = [], []
        for venta in ventas:
            if venta.por_gramo and all(
                t in historial.PRODUCTO_POR_TRAMO for t in venta.gramos
            ):
                aplicables.append(venta)
            else:
                sin_producto.append(venta)
        return aplicables, sin_producto

    def _seudonimizar(self, ventas, ruta: Path) -> dict[str, str]:
        """
        Un seudónimo estable por cliente, y el mapa escrito fuera del repositorio.

        El número se asigna por orden de primera compra, que es estable: dos
        corridas sobre el mismo archivo dan los mismos seudónimos, y eso
        importa para poder comparar resultados entre corridas.
        """
        seudonimos: dict[str, str] = {}
        for venta in ventas:
            clave = venta.cliente.strip().upper()
            if clave and clave not in seudonimos:
                seudonimos[clave] = f"Cliente {len(seudonimos) + 1:04d}"

        destino = ruta.parent / NOMBRE_DEL_MAPA
        with open(destino, "w", encoding="utf-8-sig", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["nombre_en_la_planilla", "seudonimo"])
            escritor.writerows(sorted(seudonimos.items(), key=lambda par: par[1]))

        return seudonimos

    def _cargar(self, tienda, ventas, productos, seudonimos) -> int:
        """
        Cada venta del libro pasa a ser un pedido entregado.

        Entregado y no pendiente: son ventas que ya ocurrieron y se cobraron.
        Si entraran como pendientes, los indicadores del panel las dejarían
        fuera de las ventas del mes, que es justo lo contrario de lo que son.
        """
        creados = 0
        for venta in ventas:
            pedido = self._crear_pedido(tienda, venta, seudonimos)
            for tramo, gramos in venta.gramos.items():
                producto = productos[historial.PRODUCTO_POR_TRAMO[tramo]]
                self._crear_linea(pedido, producto, venta, gramos)
            creados += 1
        return creados

    def _crear_pedido(self, tienda, venta, seudonimos) -> Pedido:
        cifras = desglose(round(venta.monto / 1.19))
        pedido = Pedido.objects.create(
            tienda=tienda,
            nombre_contacto=seudonimos.get(
                venta.cliente.strip().upper(), "Cliente sin nombre"
            ),
            telefono_contacto="No registrado",
            notas=self._marca(),
            estado=Pedido.Estado.ENTREGADO,
            total_neto=cifras["neto"],
            total_iva=cifras["iva"],
            total=cifras["total"],
        )
        # `fecha_creacion` es auto_now_add: la fecha real se pone después, o
        # todo el historial quedaría fechado hoy y no habría serie de tiempo.
        Pedido.objects.filter(pk=pedido.pk).update(
            fecha_creacion=timezone.make_aware(
                timezone.datetime.combine(venta.fecha, timezone.datetime.min.time())
            )
        )
        return pedido

    def _crear_linea(self, pedido, producto, venta, gramos) -> None:
        """
        El precio de la línea es el que **de verdad se cobró** esa vez.

        No el del catálogo de hoy: los precios subieron en dos años y usar los
        actuales reescribiría el historial. Se reparte el monto de la venta
        entre sus tramos a prorrata de los gramos de cada uno.
        """
        proporcion = gramos / sum(venta.gramos.values())
        neto = round(venta.monto / 1.19 * proporcion)
        cifras = desglose(neto)

        LineaPedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=Decimal(str(round(gramos, 2))),
            precio_unitario_neto=round(neto / gramos) if gramos else 0,
            subtotal_neto=cifras["neto"],
            subtotal_iva=cifras["iva"],
            subtotal_total=cifras["total"],
        )


def _adelantar(fecha, anos: int):
    """
    La misma fecha, tantos años después.

    En años enteros y no en meses: así cada venta cae en el mismo mes del año
    y la estacionalidad del negocio —Navidad, Día de la Madre— se mantiene
    donde estaba. Corrida en meses, el peak de diciembre aparecería en enero y
    el pronóstico aprendería una temporada que nunca existió.
    """
    try:
        return fecha.replace(year=fecha.year + anos)
    except ValueError:
        # 29 de febrero en un año que no es bisiesto.
        return fecha.replace(year=fecha.year + anos, day=28)
