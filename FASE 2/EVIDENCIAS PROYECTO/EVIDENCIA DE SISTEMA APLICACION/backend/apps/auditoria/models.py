"""
Registro de actividad: quién hizo qué, en qué tienda y cuándo.

Lo lee la administración de la plataforma para saber qué pasó en cada tienda.
Es de solo agregar: ninguna vista lo edita ni lo borra, porque un registro que
se puede corregir después no sirve para reconstruir lo que pasó.
"""

from django.conf import settings
from django.db import models


class Accion(models.TextChoices):
    CREAR = "crear", "Creó"
    MODIFICAR = "modificar", "Modificó"
    ELIMINAR = "eliminar", "Eliminó"
    SESION = "sesion", "Inició sesión"
    PLAN = "plan", "Cambió el plan"
    CUENTA = "cuenta", "Cambió su cuenta"


class Registro(models.Model):
    """
    Una acción hecha por alguien.

    No hereda de ModeloDeTienda: hay acciones de la plataforma que no son de
    ninguna tienda, y el registro tiene que sobrevivir aunque la tienda o el
    usuario se borren. Por eso los dos quedan también copiados como texto.
    """

    fecha = models.DateTimeField("fecha", auto_now_add=True, db_index=True)

    tienda = models.ForeignKey(
        "tiendas.Tienda",
        verbose_name="tienda",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros",
    )
    tienda_nombre = models.CharField("tienda (texto)", max_length=120, blank=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros",
    )
    usuario_email = models.CharField("usuario (texto)", max_length=254, blank=True)

    accion = models.CharField("acción", max_length=20, choices=Accion.choices)
    modelo = models.CharField("qué", max_length=80)
    objeto = models.CharField("cuál", max_length=200, blank=True)

    # Campo por campo, el valor anterior y el nuevo. Nunca lleva contraseñas:
    # las señales excluyen esos campos antes de llegar acá.
    detalle = models.JSONField("detalle", default=dict, blank=True)

    ip = models.GenericIPAddressField("IP", null=True, blank=True)

    class Meta:
        verbose_name = "registro de actividad"
        verbose_name_plural = "registros de actividad"
        ordering = ["-fecha", "-id"]
        indexes = [models.Index(fields=["tienda", "-fecha"])]

    def __str__(self):
        cuando = f"{self.fecha:%d-%m-%Y %H:%M}"
        return f"{cuando} {self.usuario_email} {self.accion} {self.modelo}"
