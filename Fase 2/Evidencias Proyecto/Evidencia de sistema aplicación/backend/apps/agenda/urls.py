"""Rutas públicas de la agenda."""

from django.urls import path

from apps.agenda.views import HorasDisponibles, PedirVisita

urlpatterns = [
    path(
        "t/<slug:slug>/agenda/horas",
        HorasDisponibles.as_view(),
        name="agenda-horas-disponibles",
    ),
    path(
        "t/<slug:slug>/agenda/visitas",
        PedirVisita.as_view(),
        name="agenda-pedir-visita",
    ),
]
