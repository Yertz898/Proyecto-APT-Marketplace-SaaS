"""
Quiénes compran seguido, quiénes se están yendo y quiénes ya se fueron.

Acá está **la línea base** de la segmentación: una regla por recencia. No es
el modelo; es contra qué se mide el modelo. La regla del proyecto es que
ningún clasificador entra si no le gana a su línea base (ver
`docs/analitica.md`).

Se agrupa por las tres variables de siempre —recencia, frecuencia y monto—
pero la que decide el segmento es la recencia, porque es la única que dice
algo sobre el futuro: cuánto gastó alguien el año pasado no indica si va a
volver.

**El umbral sale de los datos de cada tienda, no de un número elegido a
mano.** Se toma el percentil 90 de los días que pasan entre dos compras de un
mismo cliente: si nueve de cada diez veces alguien vuelve antes de ese plazo,
quien lo pasó rompió su propio patrón. En Joyas_ye son 104 días; en otra
tienda, con otro ritmo de compra, será otro número y la regla sigue valiendo.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.utils import timezone

from apps.pedidos.models import Pedido

#: Qué estados cuentan como compra. Igual que en el resto de la analítica.
VENDIDOS = (Pedido.Estado.CONFIRMADO, Pedido.Estado.ENTREGADO)

#: Cuántos intervalos entre compras hacen falta para calcular el umbral.
#:
#: Con menos, el percentil 90 lo decide un cliente raro. Una tienda nueva cae
#: al umbral por omisión y la pantalla lo dice.
MINIMO_DE_INTERVALOS = 20

#: Umbral para una tienda que todavía no tiene cómo calcular el suyo.
#: Un trimestre: el plazo en que un comercio minorista corriente espera ver
#: volver a un cliente.
DIAS_POR_OMISION = 90


class Segmento:
    HABITUAL = "habitual"
    NUEVO = "nuevo"
    EN_RIESGO = "en_riesgo"
    PERDIDO = "perdido"


#: Cómo se le explica cada segmento al dueño.
DESCRIPCION = {
    Segmento.HABITUAL: "Compra seguido y volvió hace poco.",
    Segmento.NUEVO: "Compró una vez y fue hace poco. Todavía no es un hábito.",
    Segmento.EN_RIESGO: "Compraba y dejó de hacerlo. Se puede recuperar.",
    Segmento.PERDIDO: "Lleva tanto sin volver que ya no se parece a un cliente activo.",
}


@dataclass(frozen=True)
class Cliente:
    nombre: str
    #: Días desde su última compra.
    recencia: int
    #: Cuántas veces compró.
    frecuencia: int
    #: Cuánto gastó en total, con IVA.
    monto: int
    segmento: str


@dataclass(frozen=True)
class Resumen:
    """La segmentación completa de una tienda."""

    #: Días sin volver a partir de los cuales se considera que alguien se fue.
    umbral: int
    #: Si el umbral se calculó con los datos de la tienda o es el por omisión.
    umbral_calculado: bool
    clientes: list[Cliente]
    metodo: str = "regla por recencia (línea base)"

    @property
    def conteo(self) -> dict[str, int]:
        cuentas = dict.fromkeys(DESCRIPCION, 0)
        for cliente in self.clientes:
            cuentas[cliente.segmento] += 1
        return cuentas


def segmentar(tienda, hoy=None) -> Resumen:
    """Cada comprador de la tienda, con su segmento."""
    # La fecha de Chile y no la del servidor: «hace cuántos días compró»
    # es una cuenta de días de calendario y tiene que usar el mismo huso
    # con que se guardaron las compras, o se desfasa un día.
    hoy = hoy or timezone.localdate()
    compras = _compras_por_cliente(tienda)
    umbral, calculado = umbral_de_abandono(compras)

    clientes = []
    for nombre, hechas in compras.items():
        fechas = sorted(f for f, _ in hechas)
        recencia = (hoy - fechas[-1]).days
        clientes.append(
            Cliente(
                nombre=nombre,
                recencia=recencia,
                frecuencia=len(hechas),
                monto=int(sum(monto for _, monto in hechas)),
                segmento=_segmento(recencia, len(hechas), umbral),
            )
        )

    # Primero quien más conviene mirar: el que más gastó y se está yendo.
    orden = {
        Segmento.EN_RIESGO: 0,
        Segmento.HABITUAL: 1,
        Segmento.NUEVO: 2,
        Segmento.PERDIDO: 3,
    }
    clientes.sort(key=lambda c: (orden[c.segmento], -c.monto))

    return Resumen(umbral=umbral, umbral_calculado=calculado, clientes=clientes)


def umbral_de_abandono(compras) -> tuple[int, bool]:
    """
    A partir de cuántos días sin volver se considera que alguien se fue.

    Es el percentil 90 de los intervalos entre compras de la tienda. Devuelve
    también si se pudo calcular: una tienda sin clientes repetidos no tiene
    patrón que romper, y conviene que la pantalla lo diga en vez de mostrar
    un umbral que parece medido.
    """
    intervalos = []
    for hechas in compras.values():
        fechas = sorted(f for f, _ in hechas)
        intervalos += [(fechas[i + 1] - fechas[i]).days for i in range(len(fechas) - 1)]

    if len(intervalos) < MINIMO_DE_INTERVALOS:
        return DIAS_POR_OMISION, False

    intervalos.sort()
    return intervalos[int(len(intervalos) * 0.9)], True


def _segmento(recencia: int, frecuencia: int, umbral: int) -> str:
    """
    Cuatro grupos, y la recencia decide.

    «Perdido» empieza al doble del umbral y no al umbral: entre uno y otro
    hay alguien a quien todavía tiene sentido escribirle, y meterlo en la
    misma bolsa que a quien se fue hace un año haría que el dueño no le
    escriba a ninguno.
    """
    if recencia > umbral * 2:
        return Segmento.PERDIDO
    if recencia > umbral:
        return Segmento.EN_RIESGO
    if frecuencia > 1:
        return Segmento.HABITUAL
    return Segmento.NUEVO


def _compras_por_cliente(tienda) -> dict[str, list[tuple[date, Decimal]]]:
    """
    Las compras de cada cliente.

    Se agrupa por el nombre de contacto del pedido y no por la cuenta del
    comprador: la mayoría compra sin registrarse, y dejar fuera a quien no
    tiene cuenta vaciaría la segmentación.
    """
    compras: dict[str, list] = defaultdict(list)
    filas = Pedido.objects.filter(tienda=tienda, estado__in=VENDIDOS).values(
        "nombre_contacto", "fecha_creacion", "total"
    )
    for fila in filas:
        nombre = (fila["nombre_contacto"] or "").strip()
        if not nombre:
            continue
        compras[nombre].append(
            (timezone.localtime(fila["fecha_creacion"]).date(), fila["total"])
        )
    return compras
