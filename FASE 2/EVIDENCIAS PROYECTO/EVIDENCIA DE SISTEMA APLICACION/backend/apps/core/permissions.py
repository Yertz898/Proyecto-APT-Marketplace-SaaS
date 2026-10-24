"""
Permisos por rol de DRF.

La autorización se resuelve en el backend, en cada endpoint. Ocultar un botón en
el frontend no protege nada.
"""

from rest_framework.permissions import BasePermission

from apps.usuarios.models import Rol


class EsAdminPlataforma(BasePermission):
    """Nosotros. Ve todas las tiendas."""

    message = "Esta acción es solo para la administración de la plataforma."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.es_admin_plataforma
        )


class TrabajaEnLaTienda(BasePermission):
    """Dueño o vendedor: administran los datos de su propia tienda."""

    message = "Esta acción es solo para el dueño o los vendedores de la tienda."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.trabaja_en_tienda
            and usuario.tienda_id
        )


class EsDuenoDeTienda(BasePermission):
    """
    Solo el dueño.

    El vendedor hace lo mismo que el dueño salvo facturación y gestión de
    usuarios; esas dos cosas piden este permiso.
    """

    message = "Esta acción es solo para el dueño de la tienda."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.rol == Rol.DUENO_TIENDA
            and usuario.tienda_id
        )


class EsComprador(BasePermission):
    """Cliente final o mayorista. No pertenece a ninguna tienda."""

    message = "Esta acción es solo para compradores."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and usuario.is_authenticated and usuario.rol == Rol.COMPRADOR
        )
