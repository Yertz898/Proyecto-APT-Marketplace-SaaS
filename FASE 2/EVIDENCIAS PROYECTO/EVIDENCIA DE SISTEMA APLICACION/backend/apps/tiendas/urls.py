"""Rutas de la tienda: las públicas de la vitrina y el perfil del panel."""

from django.urls import path

from apps.tiendas.views import PedirAcceso, PerfilDeTienda, TiendaPublica

urlpatterns = [
    path("t/<slug:slug>/tienda", TiendaPublica.as_view(), name="tienda-publica"),
    path("solicitudes-de-acceso", PedirAcceso.as_view(), name="pedir-acceso"),
    # Del panel: la tienda sale del token, por eso la ruta no la nombra.
    path("panel/tienda", PerfilDeTienda.as_view(), name="panel-perfil-tienda"),
]
