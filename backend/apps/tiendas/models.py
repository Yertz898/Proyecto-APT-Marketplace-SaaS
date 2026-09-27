"""
Tienda: cada comercio suscrito. Es la raíz del aislamiento.

Todo dato del sistema cuelga directa o indirectamente de una Tienda. Si un
modelo no puede responder a qué tienda pertenece, está mal modelado.

Su identidad visual también es dato, no código: el frontend no sabe nada de
ninguna tienda en particular.
"""

from django.db import models

from apps.tiendas.validadores import validar_color_hexadecimal


class Tienda(models.Model):
    # El slug es la identidad pública: la tienda va en la ruta /t/<slug>/.
    slug = models.SlugField("identificador público", max_length=60, unique=True)
    nombre = models.CharField("nombre", max_length=120)

    activa = models.BooleanField(
        "activa",
        default=True,
        help_text="Una tienda inactiva no se muestra al público.",
    )

    # ── Identidad visual ────────────────────────────────────────────────────
    # La base guarda la referencia del archivo, no el binario ni la URL completa.

    logo = models.ImageField("logo", upload_to="tiendas/logos/", blank=True, null=True)
    banner = models.ImageField(
        "banner", upload_to="tiendas/banners/", blank=True, null=True
    )

    # Se aplican como variables CSS. El frontend solo acepta hexadecimal, y acá
    # se valida lo mismo: todas las tiendas comparten origen, así que un valor
    # arbitrario en un color sería CSS de una tienda corriendo en la página de
    # otra.
    color_primario = models.CharField(
        "color primario",
        max_length=7,
        blank=True,
        validators=[validar_color_hexadecimal],
    )
    color_primario_hover = models.CharField(
        "color primario al pasar el mouse",
        max_length=7,
        blank=True,
        validators=[validar_color_hexadecimal],
    )
    color_acento = models.CharField(
        "color de acento",
        max_length=7,
        blank=True,
        validators=[validar_color_hexadecimal],
    )
    color_destacado = models.CharField(
        "color destacado",
        max_length=7,
        blank=True,
        validators=[validar_color_hexadecimal],
    )

    whatsapp = models.URLField("enlace de WhatsApp", blank=True)
    instagram = models.URLField("enlace de Instagram", blank=True)

    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "tienda"
        verbose_name_plural = "tiendas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
