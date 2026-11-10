"""Registro de los tramos de precio en el panel de administración."""

from django.contrib import admin

from apps.precios.models import TramoPrecio


@admin.register(TramoPrecio)
class AdminTramoPrecio(admin.ModelAdmin):
    list_display = [
        "tienda",
        "producto",
        "unidad_umbral",
        "umbral",
        "valor",
    ]
    list_filter = ["tienda", "unidad_umbral"]
    search_fields = ["producto__codigo", "producto__nombre"]
