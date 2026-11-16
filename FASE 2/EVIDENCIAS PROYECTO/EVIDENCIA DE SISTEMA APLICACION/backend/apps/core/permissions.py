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


MENSAJE_TIENDA_CERRADA = (
    "Tu tienda está cerrada por la administración de DealCommerce. "
    "Escríbenos para reabrirla."
)


def _tienda_cerrada(usuario) -> bool:
    """La tienda del usuario la cerró la administración (ver Tienda)."""
    return bool(usuario.tienda_id and usuario.tienda.cerrada_por_la_plataforma)


class TrabajaEnLaTienda(BasePermission):
    """Dueño o vendedor: administran los datos de su propia tienda."""

    message = "Esta acción es solo para el dueño o los vendedores de la tienda."

    def has_permission(self, request, view):
        usuario = request.user
        if not (
            usuario
            and usuario.is_authenticated
            and usuario.trabaja_en_tienda
            and usuario.tienda_id
        ):
            return False
        if _tienda_cerrada(usuario):
            self.message = MENSAJE_TIENDA_CERRADA
            return False
        return True


class EsDuenoDeTienda(BasePermission):
    """
    Solo el dueño.

    El vendedor hace lo mismo que el dueño salvo facturación y gestión de
    usuarios; esas dos cosas piden este permiso.
    """

    message = "Esta acción es solo para el dueño de la tienda."

    def has_permission(self, request, view):
        usuario = request.user
        if not (
            usuario
            and usuario.is_authenticated
            and usuario.rol == Rol.DUENO_TIENDA
            and usuario.tienda_id
        ):
            return False
        if _tienda_cerrada(usuario):
            self.message = MENSAJE_TIENDA_CERRADA
            return False
        return True


class EsComprador(BasePermission):
    """Cliente final o mayorista. No pertenece a ninguna tienda."""

    message = "Esta acción es solo para compradores."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and usuario.is_authenticated and usuario.rol == Rol.COMPRADOR
        )


_ESCALERA_DE_PLANES = ["basico", "premium", "ultimate"]


def plan_alcanza(plan: str, minimo: str) -> bool:
    return _ESCALERA_DE_PLANES.index(plan) >= _ESCALERA_DE_PLANES.index(minimo)


def PlanMinimo(minimo: str):  # noqa: N802 — se usa como una clase de permiso
    """
    Exige que la tienda del usuario tenga al menos este plan.

    El panel dibuja el candado, pero esconder una sección no protege nada: el
    plan se vuelve a revisar acá en cada petición.
    """

    class _PlanMinimo(BasePermission):
        message = "Tu plan no incluye esta sección."

        def has_permission(self, request, view):
            tienda = getattr(request.user, "tienda", None)
            return bool(tienda and plan_alcanza(tienda.plan, minimo))

    return _PlanMinimo
