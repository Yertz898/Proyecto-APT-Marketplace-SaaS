"""
Rutas del asistente.

Del panel, así que la tienda sale del token y la ruta no la nombra.
"""

from django.urls import path

from apps.asistente.views import Preguntar

urlpatterns = [
    path("panel/asistente", Preguntar.as_view(), name="panel-asistente"),
]
