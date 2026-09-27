"""Vistas de la API de `agenda`."""

from datetime import datetime

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agenda.disponibilidad import horas_disponibles
from apps.agenda.models import ConfiguracionAgenda
from apps.agenda.serializers import HoraDisponibleSerializer
from apps.tiendas.models import Tienda

FORMATO_FECHA = "%Y-%m-%d"


def _fecha(valor, campo):
    """Convierte un parámetro de la URL en fecha, o explica por qué no puede."""
    if not valor:
        return None

    try:
        return datetime.strptime(valor, FORMATO_FECHA).date()
    except ValueError:
        raise ValidationError({campo: "Usa el formato aaaa-mm-dd."}) from None


class HorasDisponibles(APIView):
    """
    Horas libres para agendar una visita a la oficina de la tienda.

    Es público: el comprador mira la agenda antes de iniciar sesión. Reservar sí
    va a exigir sesión, pero eso es otro endpoint.

    La tienda se resuelve por el slug de la ruta, igual que el resto de la
    vitrina pública. Una tienda inactiva, inexistente o sin agenda configurada
    responde 404.
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

        horas = horas_disponibles(
            configuracion,
            desde=_fecha(request.query_params.get("desde"), "desde"),
            hasta=_fecha(request.query_params.get("hasta"), "hasta"),
        )

        return Response(
            {
                "direccion": configuracion.direccion,
                "indicaciones": configuracion.indicaciones,
                "anticipacionMinimaHoras": configuracion.anticipacion_minima_horas,
                "horas": HoraDisponibleSerializer(horas, many=True).data,
            }
        )
