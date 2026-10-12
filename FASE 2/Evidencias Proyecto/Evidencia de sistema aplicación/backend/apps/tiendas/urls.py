"""Rutas públicas de la tienda."""

from django.urls import path

from apps.tiendas.views import PedirAcceso, TiendaPublica

urlpatterns = [
    path("t/<slug:slug>/tienda", TiendaPublica.as_view(), name="tienda-publica"),
    path("solicitudes-de-acceso", PedirAcceso.as_view(), name="pedir-acceso"),
]
