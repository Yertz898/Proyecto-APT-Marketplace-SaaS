"""
Modelos base compartidos: la relación con Tienda y los campos de auditoría.

Los modelos del dominio heredan de acá para que el campo `tienda` y su índice
existan siempre, y no dependan de que alguien recuerde agregarlos.
"""

from django.db import models

from apps.core.managers import ManagerDeTienda


class ModeloDeTienda(models.Model):
    """
    Base de todo modelo que pertenece a una tienda.

    Trae el campo `tienda` con su índice y el manager que sabe acotar por
    tienda. Las vistas nunca arman el filtro a mano: usan los mixins de
    apps.core.mixins, que llaman a este manager.
    """

    tienda = models.ForeignKey(
        "tiendas.Tienda",
        verbose_name="tienda",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)
    fecha_edicion = models.DateTimeField("última edición", auto_now=True)

    objects = ManagerDeTienda()

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["tienda"])]
