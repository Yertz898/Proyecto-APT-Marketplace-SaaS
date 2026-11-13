"""
Cuánto se va a vender el próximo mes, y qué se va a quedar sin stock.

Proyecta con **suavizado de Holt amortiguado**, el modelo que le ganó a la
línea base en la evaluación del 12-11-2026: MAPE 55,2% contra 64,8% del
promedio móvil, y también le ganó en validación (ver `docs/analitica.md` y
`modelos_pronostico.py`, que es donde se mide).

El promedio móvil sigue acá porque sigue siendo **la línea base**: todo modelo
futuro se mide contra él, y si algún día Holt deja de ganarle, se vuelve a él
cambiando una línea.

Dos cosas que este módulo se niega a hacer:

- **Proyectar sin historia suficiente.** Un producto con dos meses de ventas
  no tiene serie de tiempo, tiene dos números. Devuelve «datos insuficientes»
  y dice cuántos meses le faltan. Es la diferencia entre no saber y mentir.
- **Alertar de quiebre a quien no lleva inventario.** La tienda no sabe cuánto
  le queda de su granel, así que no hay quiebre que anunciar. Se muestra la
  proyección y nada más.

El pronóstico es **por producto**. En `docs/analitica.md` está escrito que
sería por categoría cuando el producto no tenga historia propia; en Joyas_ye
los tres productos por gramo la tienen —quince meses cada uno— y los lotes no
tienen ninguna, así que agrupar por categoría no agregaría nada: daría el
mismo «datos insuficientes» con otro nombre.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.catalogo.models import Producto
from apps.pedidos.models import LineaPedido, Pedido

#: Cuántos meses cerrados necesita un producto para que se lo proyecte.
#:
#: Seis es el mínimo con el que un promedio móvil de tres meses tiene algo
#: contra qué compararse. Con menos, la "proyección" sería repetir el último
#: mes y llamarlo pronóstico.
MINIMO_DE_MESES = 6

#: Sobre cuántos meses se promedia.
#:
#: Tres: suficiente para que un mes raro no mande, corto para que un cambio
#: de nivel se note. Es la línea base clásica y la que el Sprint Backlog
#: nombra explícitamente.
VENTANA = 3

#: Los parámetros de Holt, elegidos en validación (feb a jun de 2026).
#:
#: No se ajustan solos con cada mes nuevo: cambiarlos es volver a correr
#: `manage.py entrenar_pronostico`, mirar si sigue ganando y anotarlo en
#: `docs/analitica.md`. Un parámetro que se mueve sin que nadie lo mida es
#: un modelo que nadie evaluó.
ALFA, BETA, PHI = 0.4, 0.1, 0.8

#: Qué estados de pedido son una venta. Igual que en `ventas.py`: un pedido
#: pendiente todavía no ocurrió y uno anulado no ocurrió nunca.
VENDIDOS = (Pedido.Estado.CONFIRMADO, Pedido.Estado.ENTREGADO)


@dataclass(frozen=True)
class Proyeccion:
    """
    Lo que se espera vender de un producto el próximo mes.

    `suficiente` manda sobre todo lo demás: cuando es falso no hay
    proyección, hay un producto del que todavía no se puede decir nada.
    """

    codigo: str
    nombre: str
    unidad: str
    meses_con_ventas: int
    suficiente: bool
    #: Cantidad esperada para el próximo mes. None si no hay con qué.
    esperado: Decimal | None = None
    #: Los últimos meses, del más viejo al más nuevo: [(aaaa-mm, cantidad)].
    serie: list = None
    #: Con qué se calculó. Lo muestran la pantalla y el asistente.
    metodo: str = "suavizado de Holt amortiguado"
    #: Días hasta quedarse sin stock al ritmo proyectado. None si no aplica.
    dias_hasta_quiebre: int | None = None
    stock: Decimal | None = None


def proyectar(tienda, hoy=None) -> list[Proyeccion]:
    """La proyección de cada producto publicado de la tienda."""
    hoy = hoy or date.today()
    series = _series_por_producto(tienda, hoy)

    proyecciones = []
    for producto in Producto.objects.publicadas_de(tienda).order_by("codigo"):
        proyecciones.append(_proyectar_uno(producto, series.get(producto.pk, [])))

    # Primero lo que pide atención: lo que se queda sin stock antes.
    proyecciones.sort(
        key=lambda p: (
            p.dias_hasta_quiebre is None,
            p.dias_hasta_quiebre if p.dias_hasta_quiebre is not None else 0,
            p.codigo,
        )
    )
    return proyecciones


def _series_por_producto(tienda, hoy) -> dict[int, list[tuple[str, Decimal]]]:
    """
    Cuánto se vendió de cada producto, por mes.

    **El mes en curso queda fuera.** Va por la mitad, así que su total es
    siempre menor que el de un mes cerrado y arrastraría el promedio hacia
    abajo cada vez que se mira la pantalla.
    """
    # Con zona horaria: el campo la tiene, y una fecha desnuda la compara
    # contra UTC. A fin de mes eso corre el corte un día.
    inicio_del_mes = timezone.make_aware(
        timezone.datetime.combine(hoy.replace(day=1), timezone.datetime.min.time())
    )

    filas = (
        LineaPedido.objects.filter(
            pedido__tienda=tienda,
            pedido__estado__in=VENDIDOS,
            pedido__fecha_creacion__lt=inicio_del_mes,
        )
        .annotate(mes=TruncMonth("pedido__fecha_creacion"))
        .values("producto_id", "mes")
        .annotate(cantidad=Sum("cantidad"))
        .order_by("mes")
    )

    series: dict[int, list] = {}
    for fila in filas:
        series.setdefault(fila["producto_id"], []).append(
            (fila["mes"].strftime("%Y-%m"), fila["cantidad"])
        )
    return series


def _proyectar_uno(producto, serie) -> Proyeccion:
    comun = {
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "unidad": producto.unidad_medida,
        "meses_con_ventas": len(serie),
        "serie": serie[-12:],
    }

    if len(serie) < MINIMO_DE_MESES:
        return Proyeccion(**comun, suficiente=False)

    historia = [float(cantidad) for _, cantidad in serie]
    esperado = Decimal(str(holt_amortiguado(historia, ALFA, BETA, PHI))).quantize(
        Decimal("0.01")
    )

    return Proyeccion(
        **comun,
        suficiente=True,
        esperado=esperado,
        stock=producto.stock,
        dias_hasta_quiebre=_dias_hasta_quiebre(producto, esperado),
    )


def holt_amortiguado(historia: list[float], alfa, beta, phi) -> float:
    """
    Suavizado exponencial con tendencia amortiguada.

    Sigue el nivel y la tendencia de la serie, pero la tendencia se va
    apagando (`phi` menor que 1). Es lo que corresponde cuando no se sabe si
    una caída va a seguir: una tendencia sin amortiguar proyecta que la caída
    sigue igual para siempre, y en pocos meses pronostica cero.

    Con ventas constantes da esas mismas ventas: no inventa movimiento.
    """
    nivel = historia[0]
    tendencia = historia[1] - historia[0] if len(historia) > 1 else 0.0
    for valor in historia[1:]:
        anterior = nivel
        nivel = alfa * valor + (1 - alfa) * (nivel + phi * tendencia)
        tendencia = beta * (nivel - anterior) + (1 - beta) * phi * tendencia
    return max(nivel + phi * tendencia, 0.0)


def promedio_movil(cantidades: list[Decimal], ventana: int = VENTANA) -> Decimal:
    """
    La línea base: el promedio de los últimos meses.

    Es deliberadamente simple. Su trabajo no es acertar sino poner el listón:
    un modelo que no le gana a esto no justifica su complejidad.
    """
    ultimos = cantidades[-ventana:]
    return (sum(ultimos) / len(ultimos)).quantize(Decimal("0.01"))


def _dias_hasta_quiebre(producto, esperado: Decimal) -> int | None:
    """
    En cuántos días se acaba el stock al ritmo proyectado.

    Solo para quien lleva inventario. La tienda no registra cuánto le queda
    de lo que vende por gramo, así que ahí no hay quiebre que anunciar: un
    número inventado en una alerta de stock es peor que no tener alerta.
    """
    if not producto.controla_stock or producto.stock is None:
        return None
    if esperado <= 0:
        return None

    por_dia = esperado / Decimal(30)
    return int(producto.stock / por_dia)
