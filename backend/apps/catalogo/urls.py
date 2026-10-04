"""Rutas públicas del catálogo."""

from django.urls import path

from apps.catalogo.views import (
    DetalleDeGranel,
    DetalleDeLote,
    ListaDeGranel,
    ListaDeLotes,
)

urlpatterns = [
    path("t/<slug:slug>/lotes", ListaDeLotes.as_view(), name="catalogo-lotes"),
    path(
        "t/<slug:slug>/lotes/<str:codigo>",
        DetalleDeLote.as_view(),
        name="catalogo-lote",
    ),
    path("t/<slug:slug>/granel", ListaDeGranel.as_view(), name="catalogo-granel"),
    path(
        "t/<slug:slug>/granel/<str:codigo>",
        DetalleDeGranel.as_view(),
        name="catalogo-linea-granel",
    ),
]
