"""Vistas de la API de `agenda`."""

from datetime import datetime, timedelta

from django.core.exceptions import ValidationError as ErrorDeDjango
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agenda import avisos, cambios
from apps.agenda.disponibilidad import asiento_libre, horas_disponibles, ventana_de
from apps.agenda.models import (
    ESTADOS_VIGENTES,
    BloqueHorario,
    ConfiguracionAgenda,
    EstadoVisita,
    Visita,
)
from apps.agenda.serializers import (
    HoraDisponibleSerializer,
    MiVisitaSerializer,
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
            estado__in=ESTADOS_VIGENTES,
        ).exists():
            raise ValidationError({"inicio": "Ya tienes una visita pedida a esa hora."})

        with transaction.atomic():
            # Bloquear el bloque serializa las reservas que compiten por sus
            # cupos. El asiento numerado y su índice único son la segunda
            # defensa: aunque esto fallara, la base no deja pasarse del cupo.
            bloque = BloqueHorario.objects.select_for_update().get(pk=hora.bloque_id)
            confirma_sola = bloque.confirma_solo(configuracion)

            # Solo una visita confirmada toma asiento. Una solicitud espera a
            # que el vendedor la confirme, y es ahí donde se le busca cupo.
            asiento = 0
            if confirma_sola:
                asiento = asiento_libre(
                    tienda.pk, inicio, bloque.capacidad(configuracion)
                )
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
                    if confirma_sola
                    else EstadoVisita.SOLICITADA
                ),
                **datos,
            )

        return Response(VisitaSerializer(visita).data, status=status.HTTP_201_CREATED)


# ── Mis citas: reagendar y cancelar desde la cuenta del comprador ───────────


def _como_error_de_api(error: ErrorDeDjango) -> ValidationError:
    if hasattr(error, "error_dict"):
        return ValidationError(error.message_dict)
    return ValidationError({"detalle": error.messages})


def _mi_visita(request, slug, pk) -> Visita:
    """La visita del comprador en esa tienda, o 404: nunca la de otra persona."""
    visita = (
        Visita.objects.filter(
            pk=pk, comprador=request.user, tienda__slug=slug, tienda__activa=True
        )
        .select_related("tienda")
        .first()
    )
    if visita is None:
        raise NotFound()
    return visita


class MisVisitas(APIView):
    """
    GET /t/<slug>/agenda/mis-visitas: las visitas del comprador en la tienda.

    Primero las que siguen en pie, de la más próxima a la más lejana; después
    las pasadas o cerradas de los últimos 60 días, para que vea qué pasó con
    una que se canceló.
    """

    permission_classes = [EsComprador]

    def get(self, request, slug):
        from django.utils import timezone

        desde = timezone.now() - timedelta(days=60)
        visitas = list(
            Visita.objects.filter(
                comprador=request.user,
                tienda__slug=slug,
                tienda__activa=True,
                inicio__gte=desde,
            ).order_by("inicio")
        )
        ahora = timezone.now()
        visitas.sort(
            key=lambda v: (
                not (v.estado in ESTADOS_VIGENTES and v.fin >= ahora),
                v.inicio,
            )
        )
        return Response(MiVisitaSerializer(visitas, many=True).data)


class PropuestaDeHora(APIView):
    """POST /t/<slug>/agenda/mis-visitas/<id>/cambio  {"inicio": ...}."""

    permission_classes = [EsComprador]

    def post(self, request, slug, pk):
        from apps.agenda.panel import PropuestaDeHoraSerializer

        visita = _mi_visita(request, slug, pk)
        datos = PropuestaDeHoraSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        try:
            cambios.proponer(
                visita,
                datos.validated_data["inicio"],
                por=cambios.LadoDelCambio.COMPRADOR,
            )
        except ErrorDeDjango as error:
            raise _como_error_de_api(error) from None
        return Response(MiVisitaSerializer(visita).data, status=status.HTTP_201_CREATED)


class RespuestaAlCambio(APIView):
    """POST /t/<slug>/agenda/mis-visitas/<id>/cambio/respuesta  {"acepta": true}."""

    permission_classes = [EsComprador]

    def post(self, request, slug, pk):
        from apps.agenda.panel import RespuestaAlCambioSerializer

        visita = _mi_visita(request, slug, pk)
        datos = RespuestaAlCambioSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        cambio = cambios.pendiente_de(visita)
        if cambio is None:
            raise NotFound("Esta visita no tiene un cambio de hora pendiente.")
        try:
            visita = cambios.responder(
                cambio,
                acepta=datos.validated_data["acepta"],
                por=cambios.LadoDelCambio.COMPRADOR,
            )
        except ErrorDeDjango as error:
            raise _como_error_de_api(error) from None
        return Response(MiVisitaSerializer(visita).data)


class CancelarMiVisita(APIView):
    """POST /t/<slug>/agenda/mis-visitas/<id>/cancelar."""

    permission_classes = [EsComprador]

    def post(self, request, slug, pk):
        visita = _mi_visita(request, slug, pk)
        if visita.estado not in ESTADOS_VIGENTES:
            raise ValidationError({"visita": "Esta visita ya no se puede cancelar."})
        cambios.cancelar(visita, por=cambios.LadoDelCambio.COMPRADOR)
        return Response(MiVisitaSerializer(visita).data)


# ── El enlace del correo ────────────────────────────────────────────────────


class CambioPorEnlace(APIView):
    """
    GET/POST /agenda/cambios/enlace?firma=...

    Lo que abre el enlace de Aceptar / Rechazar del correo. La firma dice qué
    cambio es y qué lado responde, y vence en una semana: con ella no hace falta
    iniciar sesión, igual que el enlace para crear una contraseña nueva.

    GET muestra el cambio (para que la persona vea qué está aceptando) y POST
    lo responde con {"firma": ..., "acepta": true|false}.

    Mientras los correos de la agenda estén apagados nadie recibe estos
    enlaces, pero el camino ya funciona.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def _cambio(self, firma):
        from django.core import signing

        from apps.agenda.models import CambioDeHora

        try:
            datos = avisos.leer_firma(firma or "")
        except signing.BadSignature:
            raise ValidationError(
                {"firma": "El enlace venció o no es válido. Responde desde tu cuenta."}
            ) from None
        cambio = (
            CambioDeHora.objects.filter(pk=datos.get("cambio"))
            .select_related("visita", "visita__tienda")
            .first()
        )
        if cambio is None:
            raise NotFound()
        return cambio, datos.get("lado")

    def get(self, request):
        cambio, lado = self._cambio(request.query_params.get("firma"))
        visita = cambio.visita
        return Response(
            {
                "tienda": visita.tienda.nombre,
                "cliente": visita.nombre_contacto,
                "horaActual": visita.inicio,
                "horaPropuesta": cambio.inicio,
                "estado": cambio.estado,
                "responde": lado,
            }
        )

    def post(self, request):
        from apps.agenda.panel import RespuestaAlCambioSerializer

        cambio, lado = self._cambio(request.data.get("firma"))
        datos = RespuestaAlCambioSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        try:
            visita = cambios.responder(
                cambio, acepta=datos.validated_data["acepta"], por=lado
            )
        except ErrorDeDjango as error:
            raise _como_error_de_api(error) from None
        return Response({"estado": visita.estado, "inicio": visita.inicio})
