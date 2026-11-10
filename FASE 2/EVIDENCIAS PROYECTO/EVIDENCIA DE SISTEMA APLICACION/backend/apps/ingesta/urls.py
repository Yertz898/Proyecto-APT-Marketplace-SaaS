"""
Rutas de la carga masiva.

Todas del panel, así que la tienda sale del token y ninguna la nombra.
"""

from django.urls import path

from apps.ingesta.views import (
    ConfirmarCarga,
    DescartarCarga,
    HistorialDeCargas,
    LimitesDeCarga,
    PlantillaDeCarga,
    ValidarCarga,
)

urlpatterns = [
    path("panel/cargas/limites", LimitesDeCarga.as_view(), name="carga-limites"),
    path(
        "panel/plantillas/<str:tipo>",
        PlantillaDeCarga.as_view(),
        name="carga-plantilla",
    ),
    path("panel/cargas", HistorialDeCargas.as_view(), name="carga-historial"),
    path(
        "panel/cargas/<str:tipo>/validar",
        ValidarCarga.as_view(),
        name="carga-validar",
    ),
    path(
        "panel/cargas/<uuid:id>/confirmar",
        ConfirmarCarga.as_view(),
        name="carga-confirmar",
    ),
    path("panel/cargas/<uuid:id>", DescartarCarga.as_view(), name="carga-descartar"),
]
