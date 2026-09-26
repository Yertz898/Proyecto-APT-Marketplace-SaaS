"""
Tienda: cada comercio suscrito. Es la raíz del aislamiento.

Todo dato del sistema cuelga directa o indirectamente de una Tienda. Si un
modelo no puede responder a qué tienda pertenece, está mal modelado.
"""

from django.db import models


class Tienda(models.Model):
    # El slug es la identidad pública: la tienda va en la ruta /t/<slug>/.
    slug = models.SlugField("identificador público", max_length=60, unique=True)
    nombre = models.CharField("nombre", max_length=120)

    activa = models.BooleanField(
        "activa",
        default=True,
        help_text="Una tienda inactiva no se muestra al público.",
    )

    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "tienda"
        verbose_name_plural = "tiendas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
