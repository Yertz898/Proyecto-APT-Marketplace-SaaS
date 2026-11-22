"""
Los pagos con Webpay Plus.

Un pedido pagado con Webpay tiene un `Pago`: la transacción que se abrió en
Transbank, en qué terminó y lo que Transbank respondió. Un pedido coordinado
por WhatsApp no tiene ninguno, como antes.
"""

from django.db import models

from apps.core.models import ModeloDeTienda


class EstadoDelPago(models.TextChoices):
    INICIADO = "iniciado", "Esperando el pago"
    AUTORIZADO = "autorizado", "Pagado"
    RECHAZADO = "rechazado", "Rechazado"
    ABORTADO = "abortado", "Anulado por el cliente"
    VENCIDO = "vencido", "Vencido"


class Pago(ModeloDeTienda):
    pedido = models.ForeignKey(
        "pedidos.Pedido",
        verbose_name="pedido",
        on_delete=models.PROTECT,
        related_name="pagos",
    )
    # El token de Transbank identifica la transacción en el retorno.
    token = models.CharField("token de Webpay", max_length=100, unique=True)
    orden_compra = models.CharField("orden de compra", max_length=26)
    monto = models.PositiveIntegerField("monto en pesos")
    estado = models.CharField(
        "estado",
        max_length=20,
        choices=EstadoDelPago.choices,
        default=EstadoDelPago.INICIADO,
    )
    codigo_autorizacion = models.CharField(
        "código de autorización", max_length=20, blank=True
    )
    ultimos_digitos = models.CharField("últimos dígitos", max_length=4, blank=True)
    # La respuesta completa de la confirmación, para revisar un caso raro sin
    # tener que pedírsela a Transbank.
    respuesta = models.JSONField("respuesta de Transbank", default=dict, blank=True)

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "pago"
        verbose_name_plural = "pagos"
        ordering = ["-fecha_creacion"]
        indexes = [models.Index(fields=["estado", "fecha_creacion"])]

    def __str__(self):
        return f"{self.orden_compra}: {self.get_estado_display()}"
