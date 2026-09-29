"""
Cálculo de las horas disponibles para agendar una visita.

Es lógica pura sobre los datos de la tienda: recorre los días de la ventana
permitida, arma las horas de cada bloque con la duración de ese bloque y
descarta lo que no corresponde ofrecer.

Las horas se generan en hora de Chile y se devuelven en UTC. Chile cambia de
horario en abril y septiembre: generar en hora local y convertir es lo que hace
que una visita agendada antes del cambio siga siendo a las 10:00 después.

`ahora` se recibe como parámetro en vez de leerse adentro para que las pruebas
puedan situarse en cualquier fecha sin congelar el reloj del sistema.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from datetime import date as Fecha

from django.db.models import Count
from django.utils import timezone

from apps.agenda.models import ESTADOS_QUE_OCUPAN, BloqueHorario, DiaBloqueado, Visita


@dataclass(frozen=True)
class HoraDisponible:
    """Una hora concreta que el comprador puede elegir."""

    inicio: datetime
    fin: datetime
    bloque_id: int
    nombre_bloque: str
    cupos_libres: int
    confirmacion_automatica: bool


def momento_local(fecha: Fecha, hora: time) -> datetime:
    """
    Arma un instante en la hora de Chile y lo devuelve en UTC.

    La conversión se hace con la fecha puesta, así cada día usa el desfase que
    le corresponde y el cambio de horario no corre las visitas una hora.
    """
    local = datetime.combine(fecha, hora, tzinfo=timezone.get_current_timezone())
    return local.astimezone(UTC)


def _ventana(configuracion, ahora: datetime) -> tuple[datetime, datetime]:
    """Primer y último instante que la tienda acepta, como momentos exactos."""
    return (
        ahora + timedelta(hours=configuracion.anticipacion_minima_horas),
        ahora + timedelta(days=configuracion.ventana_maxima_dias),
    )


def ventana_de(configuracion, *, ahora: datetime | None = None) -> tuple[Fecha, Fecha]:
    """
    Primer y último día en que la tienda acepta visitas, en hora de Chile.

    Lo usa el endpoint para decir hasta dónde puede navegar el comprador sin
    tener que traerse todas las horas de la ventana de una vez.
    """
    ahora = ahora or timezone.now()
    zona = timezone.get_current_timezone()
    primero, ultimo = _ventana(configuracion, ahora)
    return primero.astimezone(zona).date(), ultimo.astimezone(zona).date()


def _horas_del_bloque(
    bloque: BloqueHorario, fecha: Fecha, duracion: int
) -> list[tuple[datetime, datetime]]:
    """Parte un bloque en horas consecutivas de `duracion` minutos."""
    horas = []
    paso = timedelta(minutes=duracion)

    inicio = datetime.combine(fecha, bloque.hora_inicio)
    cierre = datetime.combine(fecha, bloque.hora_fin)

    # Una hora solo se ofrece si cabe entera dentro del bloque.
    while inicio + paso <= cierre:
        fin = inicio + paso
        horas.append(
            (momento_local(fecha, inicio.time()), momento_local(fecha, fin.time()))
        )
        inicio = fin

    return horas


def _ocupacion(tienda_id: int, desde: datetime, hasta: datetime) -> dict[datetime, int]:
    """Cuántas visitas ocupan cupo en cada hora del rango."""
    conteos = (
        Visita.objects.filter(
            tienda_id=tienda_id,
            estado__in=ESTADOS_QUE_OCUPAN,
            inicio__gte=desde,
            inicio__lt=hasta,
        )
        .values("inicio")
        .annotate(total=Count("id"))
    )
    return {fila["inicio"]: fila["total"] for fila in conteos}


def horas_disponibles(
    configuracion,
    *,
    ahora: datetime | None = None,
    desde: Fecha | None = None,
    hasta: Fecha | None = None,
) -> list[HoraDisponible]:
    """
    Horas que el comprador puede elegir, ordenadas en el tiempo.

    Descarta lo que no alcanza la anticipación mínima, lo que cae fuera de la
    ventana máxima, los días bloqueados y las horas sin cupo.
    """
    ahora = ahora or timezone.now()
    tienda_id = configuracion.tienda_id

    # Ventana permitida por la configuración de la tienda.
    primer_momento, ultimo_momento = _ventana(configuracion, ahora)

    zona = timezone.get_current_timezone()
    primer_dia = primer_momento.astimezone(zona).date()
    ultimo_dia = ultimo_momento.astimezone(zona).date()

    # Un rango pedido por quien consulta solo puede achicar la ventana.
    if desde and desde > primer_dia:
        primer_dia = desde
    if hasta and hasta < ultimo_dia:
        ultimo_dia = hasta

    if primer_dia > ultimo_dia:
        return []

    bloques = list(BloqueHorario.objects.de_tienda(tienda_id))
    if not bloques:
        return []

    bloqueados = set(
        DiaBloqueado.objects.de_tienda(tienda_id)
        .filter(fecha__gte=primer_dia, fecha__lte=ultimo_dia)
        .values_list("fecha", flat=True)
    )

    ocupacion = _ocupacion(
        tienda_id,
        momento_local(primer_dia, time.min),
        momento_local(ultimo_dia + timedelta(days=1), time.min),
    )

    disponibles: list[HoraDisponible] = []
    fecha = primer_dia

    while fecha <= ultimo_dia:
        if fecha in bloqueados:
            fecha += timedelta(days=1)
            continue

        for bloque in bloques:
            if not bloque.aplica_en(fecha):
                continue

            capacidad = bloque.capacidad(configuracion)

            for inicio, fin in _horas_del_bloque(
                bloque, fecha, bloque.duracion(configuracion)
            ):
                if inicio < primer_momento or inicio > ultimo_momento:
                    continue

                libres = capacidad - ocupacion.get(inicio, 0)
                if libres <= 0:
                    continue

                disponibles.append(
                    HoraDisponible(
                        inicio=inicio,
                        fin=fin,
                        bloque_id=bloque.pk,
                        nombre_bloque=bloque.nombre,
                        cupos_libres=libres,
                        confirmacion_automatica=bloque.confirma_solo(configuracion),
                    )
                )

        fecha += timedelta(days=1)

    disponibles.sort(key=lambda hora: hora.inicio)
    return disponibles


def asiento_libre(tienda_id: int, inicio: datetime, capacidad: int) -> int | None:
    """
    Primer asiento sin tomar en esa hora, o None si está llena.

    Se usa al crear la visita, dentro de la transacción que bloquea las filas:
    el asiento numerado es lo que impide que dos reservas simultáneas se pasen
    de la capacidad.
    """
    tomados = set(
        Visita.objects.filter(
            tienda_id=tienda_id, inicio=inicio, estado__in=ESTADOS_QUE_OCUPAN
        ).values_list("posicion", flat=True)
    )

    for asiento in range(capacidad):
        if asiento not in tomados:
            return asiento

    return None
