"""Registro de los modelos de `pedidos` en el panel de administración."""

from django.contrib import admin

from apps.pedidos.models import LineaPedido, Pedido


class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 0
    readonly_fields = (
        "producto",
        "cantidad",
        "precio_unitario_neto",
        "subtotal_neto",
        "subtotal_iva",
        "subtotal_total",
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "folio",
        "tienda",
        "nombre_contacto",
        "telefono_contacto",
        "estado",
        "total",
        "creado_en",
    )
    list_filter = ("estado", "tienda", "creado_en")
    search_fields = ("folio", "nombre_contacto", "telefono_contacto")
    readonly_fields = (
        "folio",
        "total_neto",
        "total_iva",
        "total",
        "creado_en",
        "actualizado_en",
    )
    inlines = [LineaPedidoInline]
