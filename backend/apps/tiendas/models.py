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


class EstadoSolicitud(models.TextChoices):
    NUEVA = "nueva", "Nueva"
    CONTACTADA = "contactada", "Contactada"
    ACTIVADA = "activada", "Activada"
    DESCARTADA = "descartada", "Descartada"


class SolicitudDeAcceso(models.Model):
    """
    Un negocio que pidió entrar a la plataforma desde la portada.

    Es el único modelo del sistema que no cuelga de una Tienda, y no es un
    descuido: es exactamente lo que existe *antes* de que haya una. Por eso no
    hereda de ModeloDeTienda ni se acota por tienda.

    Lo escribe cualquiera desde internet, así que la vista que lo crea limita
    la frecuencia y no expone nada de vuelta salvo lo que la propia persona
    acaba de escribir.
    """

    negocio = models.CharField("nombre del negocio", max_length=150)
    nombre = models.CharField("nombre de contacto", max_length=150)

    # Único para que insistir con el mismo correo no llene la bandeja de
    # duplicados. La comparación se hace sin distinguir mayúsculas.
    email = models.EmailField("correo", unique=True)
    telefono = models.CharField("teléfono o WhatsApp", max_length=30)
    mensaje = models.TextField("qué vende", blank=True)

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.NUEVA,
    )
    notas = models.TextField("notas internas", blank=True)

    fecha_creacion = models.DateTimeField("fecha de la solicitud", auto_now_add=True)

    class Meta:
        verbose_name = "solicitud de acceso"
        verbose_name_plural = "solicitudes de acceso"
        ordering = ["-fecha_creacion"]
        indexes = [models.Index(fields=["estado", "-fecha_creacion"])]

    def __str__(self):
        return f"{self.negocio} <{self.email}>"

    def clean(self):
        super().clean()
        self.email = self.email.lower()
