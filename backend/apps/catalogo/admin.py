"""Registro del catálogo en el panel de administración."""

from django.contrib import admin

from apps.catalogo.models import Categoria, ComposicionLote, LineaGranel, Lote


class ComposicionEnLinea(admin.TabularInline):
    model = ComposicionLote
    extra = 0


@admin.register(Lote)
class AdminLote(admin.ModelAdmin):
    list_display = [
        "codigo",
        "nombre",
        "tienda",
        "precio_neto",
        "cupos_disponibles",
        "activo",
    ]
    list_filter = ["tienda", "activo", "tipo_cupo"]
    search_fields = ["codigo", "nombre"]
    inlines = [ComposicionEnLinea]


@admin.register(LineaGranel)
class AdminLineaGranel(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "tienda", "disponible"]
    list_filter = ["tienda", "disponible"]
    search_fields = ["codigo", "nombre"]
    filter_horizontal = ["categorias"]


@admin.register(Categoria)
class AdminCategoria(admin.ModelAdmin):
    list_display = ["nombre", "tienda"]
    list_filter = ["tienda"]
    search_fields = ["nombre"]
