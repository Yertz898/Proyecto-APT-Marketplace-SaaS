"""
Vistas del catálogo público.

Todo lo de acá cuelga de `/t/<slug>/`, que es la vitrina: la tienda sale de la
ruta y solo se exponen datos publicados. El filtro por tienda lo aplica
`MixinTiendaPublica`, no cada vista: repetirlo a mano es cómo se olvida en la
siguiente.

Un lote de otra tienda, inactivo o agotado responde 404 y no 403. Un 403
confirmaría que ese código existe en alguna parte, y los códigos viajan en la
URL.
"""

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.catalogo.models import LineaGranel, Lote
from apps.catalogo.serializers import LineaGranelSerializer, LoteSerializer
from apps.core.mixins import MixinTiendaPublica


class PaginaDeLotes(PageNumberPagination):
    """
    Paginación con la forma que espera el frontend.

    DRF entrega `count`, `next` y `previous`; la vitrina trabaja con el número
    de página y el total de páginas, que es lo que dibuja su paginador.
    """

    page_size = 12
    page_query_param = "pagina"
    max_page_size = 48

    def get_paginated_response(self, data):
        return Response(
            {
                "lotes": data,
                "paginaActual": self.page.number,
                "totalPaginas": self.page.paginator.num_pages,
            }
        )


class VitrinaMixin(MixinTiendaPublica):
    """La vitrina es pública y no mira el token."""

    permission_classes = [AllowAny]
    authentication_classes = []
    parametro_slug = "slug"


class ListaDeLotes(VitrinaMixin, generics.ListAPIView):
    serializer_class = LoteSerializer
    pagination_class = PaginaDeLotes
    queryset = Lote.objects.all()

    def get_queryset(self):
        return super().get_queryset().prefetch_related("composicion__categoria")


class DetalleDeLote(VitrinaMixin, generics.RetrieveAPIView):
    serializer_class = LoteSerializer
    lookup_field = "codigo"
    queryset = Lote.objects.all()

    def get_queryset(self):
        return super().get_queryset().prefetch_related("composicion__categoria")


class ListaDeGranel(VitrinaMixin, generics.ListAPIView):
    serializer_class = LineaGranelSerializer
    pagination_class = None
    queryset = LineaGranel.objects.all()

    def get_queryset(self):
        return super().get_queryset().prefetch_related("tramos")


class DetalleDeGranel(VitrinaMixin, generics.RetrieveAPIView):
    serializer_class = LineaGranelSerializer
    lookup_field = "codigo"
    queryset = LineaGranel.objects.all()

    def get_queryset(self):
        return super().get_queryset().prefetch_related("tramos")
