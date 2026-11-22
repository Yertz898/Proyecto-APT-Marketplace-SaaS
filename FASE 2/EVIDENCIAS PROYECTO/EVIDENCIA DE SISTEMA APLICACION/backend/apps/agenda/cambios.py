"""
Reagendar una visita: proponer otra hora y responder la propuesta.

Las reglas, en un lugar, para que la vitrina (el cliente), el panel (la
tienda) y el enlace del correo hagan exactamente lo mismo:

- Cualquiera de las dos partes propone una hora nueva para una visita que
  sigue en pie (solicitada o confirmada). La hora tiene que estar entre las
  que la agenda ofrece hoy: la misma comprobación que al reservar, que cubre
  anticipación, ventana, días cerrados y cupo.
- Responde **la otra** parte. Aceptar mueve la visita a la hora nueva;
  rechazar **cancela** la visita.
- Una visita confirmada que se mueve necesita cupo en la hora nueva. Se busca
  con las filas bloqueadas, igual que al confirmar, y el índice único del
  asiento es la segunda defensa.
- Cancelar o cerrar la visita anula el cambio que estuviera pendiente.

Cada paso deja su aviso registrado (`avisos.py`), que por ahora no sale por
correo: la información le llega a cada parte dentro del sistema.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.agenda import avisos
from apps.agenda.disponibilidad import (
    asiento_libre,
    capacidad_de_la_hora,
    horas_disponibles,
)
from apps.agenda.models import (
    ESTADOS_VIGENTES,
    CambioDeHora,
    ConfiguracionAgenda,
    EstadoDelCambio,
    EstadoVisita,
    LadoDelCambio,
    Visita,
)


def pendiente_de(visita: Visita) -> CambioDeHora | None:
    return visita.cambios.filter(estado=EstadoDelCambio.PENDIENTE).first()


def asiento_en(tienda_id: int, inicio) -> int:
    """
    Un cupo libre a esa hora para una visita confirmada, o error si no queda.

    Hay que llamarla dentro de una transacción: bloquea las visitas de esa hora
    para que dos confirmaciones simultáneas no tomen el mismo cupo.
    """
    configuracion, _ = ConfiguracionAgenda.objects.get_or_create(tienda_id=tienda_id)
    list(
        Visita.objects.select_for_update()
        .filter(tienda_id=tienda_id, inicio=inicio)
        .values_list("pk", flat=True)
    )
    capacidad = capacidad_de_la_hora(configuracion, inicio)
    asiento = asiento_libre(tienda_id, inicio, capacidad)
    if asiento is None:
        raise ValidationError(
            {
                "estado": "Esa hora ya está tomada por otra visita confirmada. "
                "Rechaza esta o propón otra hora."
            }
        )
    return asiento


def proponer(visita: Visita, inicio, *, por: str) -> CambioDeHora:
    """Crea la propuesta de cambio. Lanza ValidationError si no se puede."""
    if visita.estado not in ESTADOS_VIGENTES:
        raise ValidationError({"visita": "Esta visita ya no se puede reagendar."})
    if pendiente_de(visita):
        raise ValidationError(
            {"visita": "Ya hay un cambio de hora esperando respuesta para esta visita."}
        )
    if inicio == visita.inicio:
        raise ValidationError({"inicio": "Elige una hora distinta a la actual."})

    configuracion = ConfiguracionAgenda.objects.filter(
        tienda_id=visita.tienda_id
    ).first()
    hora = None
    if configuracion is not None:
        hora = next(
            (h for h in horas_disponibles(configuracion) if h.inicio == inicio), None
        )
    if hora is None:
        raise ValidationError({"inicio": "Esa hora no está disponible. Elige otra."})

    try:
        cambio = CambioDeHora.objects.create(
            tienda_id=visita.tienda_id,
            visita=visita,
            inicio=inicio,
            fin=hora.fin,
            propuesto_por=por,
        )
    except IntegrityError:
        # Las dos partes propusieron a la vez: gana la primera.
        raise ValidationError(
            {"visita": "Ya hay un cambio de hora esperando respuesta para esta visita."}
        ) from None

    avisos.cambio_propuesto(cambio)
    return cambio


def responder(cambio: CambioDeHora, *, acepta: bool, por: str) -> Visita:
    """
    Acepta o rechaza la propuesta. Rechazar cancela la visita.

    `por` es el lado que responde, y tiene que ser el contrario al que propuso.
    """
    if cambio.estado != EstadoDelCambio.PENDIENTE:
        raise ValidationError({"cambio": "Este cambio de hora ya fue respondido."})
    if por != cambio.responde:
        raise ValidationError(
            {
                "cambio": "La respuesta le toca a la otra parte, "
                "no a quien propuso el cambio."
            }
        )

    visita = cambio.visita
    try:
        with transaction.atomic():
            if acepta:
                posicion = 0
                if visita.estado == EstadoVisita.CONFIRMADA:
                    posicion = asiento_en(visita.tienda_id, cambio.inicio)
                visita.reprogramar(cambio.inicio, cambio.fin, posicion)
                visita.save()
                cambio.estado = EstadoDelCambio.ACEPTADO
            else:
                visita.cambiar_estado(EstadoVisita.CANCELADA)
                visita.save()
                cambio.estado = EstadoDelCambio.RECHAZADO
            cambio.respondido_en = timezone.now()
            cambio.save(update_fields=["estado", "respondido_en"])
    except IntegrityError:
        raise ValidationError(
            {
                "estado": "Esa hora se acaba de tomar. "
                "Rechaza el cambio o propón otra hora."
            }
        ) from None

    if acepta:
        avisos.cambio_aceptado(cambio)
    else:
        avisos.visita_cancelada(visita, por=por)
    return visita


def cancelar(visita: Visita, *, por: str, motivo: str = "") -> Visita:
    """Cancela la visita, anula el cambio pendiente y avisa a la otra parte."""
    visita.cambiar_estado(EstadoVisita.CANCELADA, motivo_rechazo=motivo)
    with transaction.atomic():
        visita.save()
        anular_pendiente(visita)
    avisos.visita_cancelada(visita, por=por, motivo=motivo)
    return visita


def anular_pendiente(visita: Visita) -> None:
    """Una visita que se cierra no deja propuestas de cambio colgando."""
    visita.cambios.filter(estado=EstadoDelCambio.PENDIENTE).update(
        estado=EstadoDelCambio.ANULADO, respondido_en=timezone.now()
    )


def representar(cambio: CambioDeHora | None) -> dict | None:
    """El cambio pendiente como lo leen las pantallas."""
    if cambio is None:
        return None
    return {
        "id": cambio.pk,
        "inicio": cambio.inicio,
        "fin": cambio.fin,
        "propuestoPor": cambio.propuesto_por,
    }


__all__ = [
    "LadoDelCambio",
    "anular_pendiente",
    "asiento_en",
    "cancelar",
    "pendiente_de",
    "proponer",
    "representar",
    "responder",
]
