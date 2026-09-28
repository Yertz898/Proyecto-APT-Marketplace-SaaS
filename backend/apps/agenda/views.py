"""Vistas de la API de `agenda`."""

from datetime import datetime, timedelta

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agenda.disponibilidad import asiento_libre, horas_disponibles, ventana_de
from apps.agenda.models import (
    ESTADOS_QUE_OCUPAN,
    BloqueHorario,
    ConfiguracionAgenda,
    EstadoVisita,
    Visita,
)
from apps.agenda.serializers import (
    HoraDisponibleSerializer,
    SolicitudDeVisitaSerializer,
    VisitaSerializer,
)
from apps.core.permissions import EsComprador
from apps.tiendas.models import Tienda

FORMATO_FECHA = "%Y-%m-%d"

#: Tope de días que se pueden pedir de una vez. La ventana de la tienda ya
#: acota el total, pero un `dias` enorme obligaría a armar miles de horas para
#: una sola pantalla.
MAXIMO_DIAS_POR_CONSULTA = 31


def _fecha(valor, campo):
    """Convierte un parámetro de la URL en fecha, o explica por qué no puede."""
    if not valor:
        return None

    try:
        return datetime.strptime(valor, FORMATO_FECHA).date()
    except ValueError:
        raise ValidationError({campo: "Usa el formato aaaa-mm-dd."}) from None


def _dias(valor):
    """Cuántos días pide la pantalla a partir del primer día del rango."""
    if not valor:
        return None

    try:
        dias = int(valor)
    except ValueError:
        raise ValidationError({"dias": "Tiene que ser un número entero."}) from None

    if not 1 <= dias <= MAXIMO_DIAS_POR_CONSULTA:
        raise ValidationError(
            {"dias": f"Tiene que estar entre 1 y {MAXIMO_DIAS_POR_CONSULTA}."}
        )

    return dias


class HorasDisponibles(APIView):
    """
    Horas libres para agendar una visita a la oficina de la tienda.

    Es público: el comprador mira la agenda antes de iniciar sesión. Reservar sí
    va a exigir sesión, pero eso es otro endpoint.

    La tienda se resuelve por el slug de la ruta, igual que el resto de la
    vitrina pública. Una tienda inactiva, inexistente o sin agenda configurada
    responde 404.

    La respuesta trae dos rangos y no son lo mismo: `ventana` es todo lo que la
    tienda acepta, y `rango` es el pedazo que se está devolviendo. Con los dos,
    la pantalla sabe si quedan días hacia atrás o hacia adelante sin tener que
    repetir acá el cálculo de la ventana.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, slug):
        _, configuracion = _tienda_con_agenda(slug)

        pedido_desde = _fecha(request.query_params.get("desde"), "desde")
        pedido_hasta = _fecha(request.query_params.get("hasta"), "hasta")
        dias = _dias(request.query_params.get("dias"))

        primer_dia, ultimo_dia = ventana_de(configuracion)

        # Lo que pida quien consulta solo puede achicar la ventana, nunca
        # estirarla: la anticipación y el tope de días son reglas de la tienda.
        desde = max(pedido_desde or primer_dia, primer_dia)
        if dias:
            hasta = desde + timedelta(days=dias - 1)
        else:
            hasta = pedido_hasta or ultimo_dia
        hasta = min(hasta, ultimo_dia)

        horas = horas_disponibles(configuracion, desde=desde, hasta=hasta)

        return Response(
            {
                "direccion": configuracion.direccion,
                "indicaciones": configuracion.indicaciones,
                "anticipacionMinimaHoras": configuracion.anticipacion_minima_horas,
                "ventana": {"desde": primer_dia, "hasta": ultimo_dia},
                "rango": {"desde": desde, "hasta": hasta},
                "horas": HoraDisponibleSerializer(horas, many=True).data,
            }
        )


def _tienda_con_agenda(slug):
    """La tienda de la ruta y su configuración, o 404 si no recibe visitas."""
    try:
        tienda = Tienda.objects.get(slug=slug, activa=True)
    except Tienda.DoesNotExist:
        raise NotFound() from None

    configuracion = ConfiguracionAgenda.objects.de_tienda(tienda).first()
    if configuracion is None:
        raise NotFound("Esta tienda no recibe visitas con hora.")

    return tienda, configuracion


class PedirVisita(APIView):
    """
    Reserva de una hora.

    Pide sesión de comprador. Mirar la agenda no la necesita, reservar sí: la
    visita queda a nombre de alguien y la tienda tiene que poder responderle.

    La hora que llega en el cuerpo no se acepta porque sí: se vuelve a calcular
    la disponibilidad y tiene que estar entre las ofrecidas. Esa sola
    comprobación cubre la anticipación mínima, la ventana, los días bloqueados,
    que el bloque exista y que quede cupo, sin repetir ninguna de esas reglas.
    """

    permission_classes = [EsComprador]

    def post(self, request, slug):
        tienda, configuracion = _tienda_con_agenda(slug)

        solicitud = SolicitudDeVisitaSerializer(data=request.data)
        solicitud.is_valid(raise_exception=True)
        datos = solicitud.validated_data
        inicio = datos.pop("inicio")

        hora = next(
            (
                disponible
                for disponible in horas_disponibles(configuracion)
                if disponible.inicio == inicio
            ),
            None,
        )
        if hora is None:
            raise ValidationError(
                {"inicio": "Esa hora ya no está disponible. Elige otra."}
            )

        # Una misma persona pidiendo dos veces la misma hora casi siempre es un
        # botón apretado dos veces, no dos visitas.
        if Visita.objects.filter(
            tienda=tienda,
            comprador=request.user,
            inicio=inicio,
            estado__in=ESTADOS_QUE_OCUPAN,
        ).exists():
            raise ValidationError({"inicio": "Ya tienes una visita pedida a esa hora."})

        with transaction.atomic():
            # Bloquear el bloque serializa las reservas que compiten por sus
            # cupos. El asiento numerado y su índice único son la segunda
            # defensa: aunque esto fallara, la base no deja pasarse del cupo.
            bloque = BloqueHorario.objects.select_for_update().get(pk=hora.bloque_id)

            asiento = asiento_libre(tienda.pk, inicio, bloque.capacidad(configuracion))
            if asiento is None:
                raise ValidationError(
                    {"inicio": "Esa hora se acaba de ocupar. Elige otra."}
                )

            visita = Visita.objects.create(
                tienda=tienda,
                comprador=request.user,
                inicio=inicio,
                fin=hora.fin,
                posicion=asiento,
                estado=(
                    EstadoVisita.CONFIRMADA
                    if bloque.confirma_solo(configuracion)
                    else EstadoVisita.SOLICITADA
                ),
                **datos,
            )

        return Response(VisitaSerializer(visita).data, status=status.HTTP_201_CREATED)
