"""
Registro de los modelos de `tiendas` en el panel de administración.

Las solicitudes de acceso se leen desde acá: es la bandeja donde llega lo que
la gente escribe en la portada.
"""

from django.contrib import admin

from apps.tiendas.models import SolicitudDeAcceso, Tienda


@admin.register(Tienda)
class AdminTienda(admin.ModelAdmin):
    list_display = ["nombre", "slug", "activa", "fecha_creacion"]
    list_filter = ["activa"]
    search_fields = ["nombre", "slug"]
    prepopulated_fields = {"slug": ["nombre"]}


@admin.register(SolicitudDeAcceso)
class AdminSolicitudDeAcceso(admin.ModelAdmin):
    list_display = [
        "negocio",
        "nombre",
        "email",
        "telefono",
        "estado",
        "fecha_creacion",
    ]
    list_filter = ["estado", "fecha_creacion"]
    search_fields = ["negocio", "nombre", "email"]
    # Lo que escribió la persona no se edita desde acá: se responde. Lo que sí
    # se toca es en qué va la conversación.
    readonly_fields = [
        "negocio",
        "nombre",
        "email",
        "telefono",
        "mensaje",
        "fecha_creacion",
    ]
    list_editable = ["estado"]
