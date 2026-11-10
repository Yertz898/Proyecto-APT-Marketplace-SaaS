"""
Rutas de analítica.

Todas del panel, así que la tienda sale del token y ninguna la nombra.
"""

from django.urls import path

from apps.analitica.views import ResumenDeVentas

urlpatterns = [
    path("panel/ventas", ResumenDeVentas.as_view(), name="panel-ventas"),
]
