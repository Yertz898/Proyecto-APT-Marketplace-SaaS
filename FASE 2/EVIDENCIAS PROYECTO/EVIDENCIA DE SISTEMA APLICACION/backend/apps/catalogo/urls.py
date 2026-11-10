"""Rutas del catálogo: las públicas de la vitrina y las del panel."""

from django.urls import path

from apps.catalogo.views import (
    CatalogoDelPanel,
    CategoriaDelPanel,
    CategoriasDelPanel,
    CotizarProducto,
    DetalleDeProducto,
    FormasDeVenta,
    InventarioDelPanel,
    ListaDeProductos,
    ProductoDelPanel,
    TramoDelPanel,
    TramosDelProducto,
)

urlpatterns = [
    # Del panel: la tienda sale del token, por eso la ruta no la nombra.
    path("panel/productos", CatalogoDelPanel.as_view(), name="panel-productos"),
    path(
        "panel/productos/<str:codigo>",
        ProductoDelPanel.as_view(),
        name="panel-producto",
    ),
    path(
        "panel/productos/<str:codigo>/tramos",
        TramosDelProducto.as_view(),
        name="panel-tramos",
    ),
    path("panel/tramos/<int:pk>", TramoDelPanel.as_view(), name="panel-tramo"),
    path("panel/categorias", CategoriasDelPanel.as_view(), name="panel-categorias"),
    path(
        "panel/categorias/<int:pk>",
        CategoriaDelPanel.as_view(),
        name="panel-categoria",
    ),
    path("panel/inventario", InventarioDelPanel.as_view(), name="panel-inventario"),
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
