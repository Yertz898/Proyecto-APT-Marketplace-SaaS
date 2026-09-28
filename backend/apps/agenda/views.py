"""Vistas de la API de `agenda`."""

from datetime import datetime, timedelta

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agenda.disponibilidad import horas_disponibles, ventana_de
from apps.agenda.models import ConfiguracionAgenda
from apps.agenda.serializers import HoraDisponibleSerializer
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
        try:
            tienda = Tienda.objects.get(slug=slug, activa=True)
        except Tienda.DoesNotExist:
            raise NotFound() from None

        configuracion = ConfiguracionAgenda.objects.de_tienda(tienda).first()
        if configuracion is None:
            raise NotFound("Esta tienda no recibe visitas con hora.")

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
