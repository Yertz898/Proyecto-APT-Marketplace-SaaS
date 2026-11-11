"""
Rutas de analítica.

Todas del panel, así que la tienda sale del token y ninguna la nombra.
"""

from django.urls import path

from apps.analitica.views import (
    PronosticoDeDemanda,
    ResumenDeVentas,
    SegmentosDeCompradores,
)

urlpatterns = [
    path("panel/ventas", ResumenDeVentas.as_view(), name="panel-ventas"),
    path("panel/pronostico", PronosticoDeDemanda.as_view(), name="panel-pronostico"),
    path("panel/segmentos", SegmentosDeCompradores.as_view(), name="panel-segmentos"),
]
