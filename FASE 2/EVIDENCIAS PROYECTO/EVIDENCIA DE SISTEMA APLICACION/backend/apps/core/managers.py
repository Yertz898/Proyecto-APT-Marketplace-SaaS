"""
Managers y querysets que acotan el acceso a la tienda del usuario autenticado.

Acá vive el filtro por tienda, una sola vez. Ningún modelo con `tienda` debe
exponer un queryset sin filtrar a una vista: `Model.objects.all()` sobre una
tabla multi-tienda es el error que este módulo existe para impedir.
"""

from django.db import models


class QuerySetDeTienda(models.QuerySet):
    def de_tienda(self, tienda):
        """Filas de una tienda concreta."""
        return self.filter(tienda=tienda)

    def de_usuario(self, usuario):
        """
        Filas que este usuario puede ver.

        - Administrador de plataforma: todas las tiendas.
        - Dueño y vendedor: solo la suya.
        - Cualquier otro caso, incluido el anónimo: nada.

        Devolver vacío en vez de lanzar un error es deliberado: así una vista
        mal escrita muestra una lista vacía o responde 404, y nunca datos de
        otra tienda.
        """
        if usuario is None or not usuario.is_authenticated:
            return self.none()

        if getattr(usuario, "es_admin_plataforma", False):
            return self

        if getattr(usuario, "trabaja_en_tienda", False) and usuario.tienda_id:
            return self.filter(tienda_id=usuario.tienda_id)

        return self.none()

    def publicadas_de(self, tienda):
        """
        Filas visibles en la tienda pública.

        Los modelos que tengan estado de publicación deben sobrescribir este
        método; por omisión, lo público es lo de esa tienda.
        """
        return self.de_tienda(tienda)


class ManagerDeTienda(models.Manager.from_queryset(QuerySetDeTienda)):
    """Manager por omisión de todo modelo que pertenezca a una tienda."""
