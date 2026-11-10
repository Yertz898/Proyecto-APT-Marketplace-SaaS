"""
Vistas de la API de `analitica`.

La tienda sale del token, nunca de la URL: lo que se devuelve acá es cuánto
vende un negocio, que es de lo más privado que guarda la plataforma.
"""

from rest_framework import generics
from rest_framework.response import Response

from apps.analitica import ventas
from apps.core.permissions import TrabajaEnLaTienda


class ResumenDeVentas(generics.GenericAPIView):
    """
    GET /api/panel/ventas

    Lo que la tienda vendió: el mes en curso contra el anterior, lo que falta
    coordinar, los productos que más dejaron y los que llevan tiempo quietos.

    Son hechos sumados de pedidos existentes. Lo estimado —pronóstico de
    demanda, segmentos— no se mezcla acá: en una misma pantalla nadie
    distinguiría qué está medido y qué está proyectado.
    """

    permission_classes = [TrabajaEnLaTienda]

    def get(self, request):
        return Response(ventas.resumen(request.user.tienda))
