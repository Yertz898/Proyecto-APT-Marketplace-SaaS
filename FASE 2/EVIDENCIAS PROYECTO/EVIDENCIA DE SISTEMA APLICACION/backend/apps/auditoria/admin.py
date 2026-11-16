from django.contrib import admin

from apps.auditoria.models import Registro


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = [
        "fecha",
        "tienda_nombre",
        "usuario_email",
        "accion",
        "modelo",
        "objeto",
    ]
    list_filter = ["accion", "modelo"]
    search_fields = ["tienda_nombre", "usuario_email", "objeto"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
