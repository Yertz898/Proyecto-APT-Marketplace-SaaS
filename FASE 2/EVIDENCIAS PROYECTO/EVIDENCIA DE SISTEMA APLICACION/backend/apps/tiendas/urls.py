"""Rutas de la tienda: la vitrina, el perfil y el plan del panel, y la plataforma."""

from django.urls import path

from apps.tiendas.mensajes import (
    EscribirALaPlataforma,
    MensajeDePlataforma,
    MensajesDePlataforma,
)
from apps.tiendas.plan import CancelarPlan, PlanDeLaTienda, ReanudarPlan
from apps.tiendas.plataforma import (
    RegistrosDePlataforma,
    SolicitudDePlataforma,
    SolicitudesDePlataforma,
    TiendaDePlataforma,
    TiendasDePlataforma,
)
from apps.tiendas.views import PedirAcceso, PerfilDeTienda, TiendaPublica

urlpatterns = [
    path("t/<slug:slug>/tienda", TiendaPublica.as_view(), name="tienda-publica"),
    path("solicitudes-de-acceso", PedirAcceso.as_view(), name="pedir-acceso"),
    # Del panel: la tienda sale del token, por eso la ruta no la nombra.
    path("panel/tienda", PerfilDeTienda.as_view(), name="panel-perfil-tienda"),
    path("panel/plan", PlanDeLaTienda.as_view(), name="panel-plan"),
    path("panel/plan/cancelar", CancelarPlan.as_view(), name="panel-plan-cancelar"),
    path("panel/plan/reanudar", ReanudarPlan.as_view(), name="panel-plan-reanudar"),
    # De la administración de la plataforma.
    path(
        "plataforma/tiendas", TiendasDePlataforma.as_view(), name="plataforma-tiendas"
    ),
    path(
        "plataforma/tiendas/<slug:slug>",
        TiendaDePlataforma.as_view(),
        name="plataforma-tienda",
    ),
    path(
        "plataforma/solicitudes",
        SolicitudesDePlataforma.as_view(),
        name="plataforma-solicitudes",
    ),
    path(
        "plataforma/solicitudes/<int:pk>",
        SolicitudDePlataforma.as_view(),
        name="plataforma-solicitud",
    ),
    path(
        "auth/mensaje-a-la-plataforma",
        EscribirALaPlataforma.as_view(),
        name="mensaje-a-la-plataforma",
    ),
    path(
        "plataforma/mensajes",
        MensajesDePlataforma.as_view(),
        name="plataforma-mensajes",
    ),
    path(
        "plataforma/mensajes/<int:pk>",
        MensajeDePlataforma.as_view(),
        name="plataforma-mensaje",
    ),
    path(
        "plataforma/registros",
        RegistrosDePlataforma.as_view(),
        name="plataforma-registros",
    ),
]
