"""Rutas públicas del catálogo."""

from django.urls import path

from apps.catalogo.views import (
    CotizarProducto,
    DetalleDeProducto,
    FormasDeVenta,
    ListaDeProductos,
)

urlpatterns = [
    path(
        "t/<slug:slug>/formas-de-venta",
        FormasDeVenta.as_view(),
        name="catalogo-formas-de-venta",
    ),
    path(
        "t/<slug:slug>/productos",
        ListaDeProductos.as_view(),
        name="catalogo-productos",
    ),
    path(
        "t/<slug:slug>/productos/<str:codigo>",
        DetalleDeProducto.as_view(),
        name="catalogo-producto",
    ),
    path(
        "t/<slug:slug>/productos/<str:codigo>/cotizar",
        CotizarProducto.as_view(),
        name="catalogo-cotizar",
    ),
]
