"""Rutas de la agenda: las públicas de la vitrina y las del panel."""

from django.urls import path

from apps.agenda.panel import (
    BloqueDeAgenda,
    BloquesDeAgenda,
    ConfiguracionDeAgenda,
    DiaBloqueadoDetalle,
    DiasBloqueados,
    EstadoDeVisita,
    ProponerCambioDesdePanel,
    ResponderCambioDesdePanel,
    VisitasDeLaTienda,
)
from apps.agenda.views import (
    CambioPorEnlace,
    CancelarMiVisita,
    HorasDisponibles,
    MisVisitas,
    PedirVisita,
    PropuestaDeHora,
    RespuestaAlCambio,
)

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
        "t/<slug:slug>/agenda/mis-visitas",
        MisVisitas.as_view(),
        name="agenda-mis-visitas",
    ),
    path(
        "t/<slug:slug>/agenda/mis-visitas/<int:pk>/cambio",
        PropuestaDeHora.as_view(),
        name="agenda-proponer-cambio",
    ),
    path(
        "t/<slug:slug>/agenda/mis-visitas/<int:pk>/cambio/respuesta",
        RespuestaAlCambio.as_view(),
        name="agenda-responder-cambio",
    ),
    path(
        "t/<slug:slug>/agenda/mis-visitas/<int:pk>/cancelar",
        CancelarMiVisita.as_view(),
        name="agenda-cancelar-visita",
    ),
    path(
        "agenda/cambios/enlace",
        CambioPorEnlace.as_view(),
        name="agenda-cambio-por-enlace",
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
    path(
        "panel/agenda/visitas/<int:pk>/cambio",
        ProponerCambioDesdePanel.as_view(),
        name="panel-agenda-proponer-cambio",
    ),
    path(
        "panel/agenda/visitas/<int:pk>/cambio/respuesta",
        ResponderCambioDesdePanel.as_view(),
        name="panel-agenda-responder-cambio",
    ),
]
