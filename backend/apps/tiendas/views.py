"""Vistas de la API de `tiendas`."""

from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.tiendas.models import Tienda
from apps.tiendas.serializers import TiendaPublicaSerializer


class TiendaPublica(generics.RetrieveAPIView):
    """
    Identidad de una tienda para su vitrina pública.

    Es el único endpoint abierto sin sesión, porque la vitrina la ve cualquiera.
    La tienda se resuelve por el slug de la ruta, que es lo que corresponde para
    el catálogo público (CONVENCIONES.md > Cómo se resuelve la tienda en cada
    petición). Todo lo demás sigue sacando la tienda del token.

    Una tienda inactiva o inexistente responde 404, sin distinguir entre las dos
    cosas: decir cuál es cuál confirmaría qué slugs existen.
    """

    serializer_class = TiendaPublicaSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    lookup_field = "slug"
    queryset = Tienda.objects.filter(activa=True)
