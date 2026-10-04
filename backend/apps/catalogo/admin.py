"""Registro del catálogo en el panel de administración."""

from django.contrib import admin

from apps.catalogo.models import Categoria, ComposicionLote, Producto


class ComposicionEnLinea(admin.TabularInline):
    model = ComposicionLote
    extra = 0


@admin.register(Producto)
class AdminProducto(admin.ModelAdmin):
    list_display = [
        "codigo",
        "nombre",
        "tienda",
        "forma_venta",
        "precio_neto",
        "stock",
        "activo",
    ]
    list_filter = ["tienda", "activo", "forma_venta", "controla_stock"]
    search_fields = ["codigo", "nombre"]
    inlines = [ComposicionEnLinea]


@admin.register(Categoria)
class AdminCategoria(admin.ModelAdmin):
    list_display = ["nombre", "tienda"]
    list_filter = ["tienda"]
    search_fields = ["nombre"]
