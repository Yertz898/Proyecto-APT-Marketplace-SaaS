"""
Clientes compradores y su relación con cada tienda.

Las variables de recencia, frecuencia y monto (RFM) se calculan sobre estos
datos y alimentan el modelo de segmentación.
"""

from django.db import models

from apps.core.models import ModeloDeTienda


class EstadoMayorista(models.TextChoices):
    SIN_SOLICITAR = "sin_solicitar", "Sin solicitar"
    PENDIENTE = "pendiente", "Pendiente de aprobación"
    APROBADO = "aprobado", "Aprobado"
    RECHAZADO = "rechazado", "Rechazado"


class AprobacionMayorista(ModeloDeTienda):
    """
    Estado mayorista de un comprador **en una tienda**.

    La aprobación es por tienda: que Joyas_ye apruebe a un comprador no lo
    aprueba en otra tienda. De acá sale la regla de qué precios puede ver
    (CLAUDE.md > Precio mayorista), que se aplica en el backend al calcular el
    precio y no ocultando nada en el frontend.
    """

    comprador = models.ForeignKey(
        "usuarios.Usuario",
        verbose_name="comprador",
        on_delete=models.CASCADE,
        related_name="aprobaciones_mayoristas",
    )

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=EstadoMayorista.choices,
        default=EstadoMayorista.SIN_SOLICITAR,
    )

    fecha_resolucion = models.DateTimeField(
        "fecha de resolución", blank=True, null=True
    )

    resuelta_por = models.ForeignKey(
        "usuarios.Usuario",
        verbose_name="resuelta por",
        on_delete=models.SET_NULL,
        related_name="aprobaciones_resueltas",
        blank=True,
        null=True,
    )

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "aprobación mayorista"
        verbose_name_plural = "aprobaciones mayoristas"
        constraints = [
            models.UniqueConstraint(
                fields=["tienda", "comprador"],
                name="aprobacion_unica_por_tienda_y_comprador",
            ),
        ]

    def __str__(self):
        return f"{self.comprador} en {self.tienda}: {self.get_estado_display()}"

    @property
    def aprobado(self) -> bool:
        return self.estado == EstadoMayorista.APROBADO
