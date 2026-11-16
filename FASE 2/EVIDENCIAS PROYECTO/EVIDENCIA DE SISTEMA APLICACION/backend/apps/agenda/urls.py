"""Rutas de la agenda: las públicas de la vitrina y las del panel."""

from django.urls import path

from apps.agenda.panel import (
    BloqueDeAgenda,
    BloquesDeAgenda,
    ConfiguracionDeAgenda,
    DiaBloqueadoDetalle,
    DiasBloqueados,
    EstadoDeVisita,
    VisitasDeLaTienda,
)
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
    path(
        "panel/agenda/configuracion",
        ConfiguracionDeAgenda.as_view(),
        name="panel-agenda-configuracion",
    ),
    path(
        "panel/agenda/bloques", BloquesDeAgenda.as_view(), name="panel-agenda-bloques"
    ),
    path(
        "panel/agenda/bloques/<int:pk>",
        BloqueDeAgenda.as_view(),
        name="panel-agenda-bloque",
    ),
    path(
        "panel/agenda/dias-cerrados",
        DiasBloqueados.as_view(),
        name="panel-agenda-dias-cerrados",
    ),
    path(
        "panel/agenda/dias-cerrados/<int:pk>",
        DiaBloqueadoDetalle.as_view(),
        name="panel-agenda-dia-cerrado",
    ),
    path(
        "panel/agenda/visitas", VisitasDeLaTienda.as_view(), name="panel-agenda-visitas"
    ),
    path(
        "panel/agenda/visitas/<int:pk>/estado",
        EstadoDeVisita.as_view(),
        name="panel-agenda-visita-estado",
    ),
]
