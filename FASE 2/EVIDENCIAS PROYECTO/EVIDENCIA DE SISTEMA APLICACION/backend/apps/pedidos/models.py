import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from apps.catalogo.models import Producto
from apps.core.models import ModeloDeTienda


class Pedido(ModeloDeTienda):
    """
    Representa una orden de compra generada en la tienda.
    El checkout es simulado: no procesa pagos en línea, el pago se coordina
    fuera de la plataforma (por ejemplo, vía WhatsApp).
    """

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", _("Pendiente de coordinación")
        CONFIRMADO = "CONFIRMADO", _("Confirmado")
        ENTREGADO = "ENTREGADO", _("Entregado")
        CANCELADO = "CANCELADO", _("Cancelado")

    # Folio público legible para compartir por WhatsApp
    folio = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        verbose_name=_("Folio del pedido"),
        help_text=_("Identificador único público (ej: DC-A1B2C3D4)"),
    )

    # Comprador autenticado (opcional para permitir compras con o sin cuenta)
    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        verbose_name=_("Comprador"),
    )

    # Datos del cliente para coordinar el despacho y pago externo
    nombre_contacto = models.CharField(
        max_length=150, verbose_name=_("Nombre de contacto")
    )
    telefono_contacto = models.CharField(
        max_length=30, verbose_name=_("Teléfono / WhatsApp")
    )
    email_contacto = models.EmailField(
        blank=True, default="", verbose_name=_("Correo electrónico")
    )
    direccion_entrega = models.CharField(
        max_length=255, blank=True, default="", verbose_name=_("Dirección de entrega")
    )
    notas = models.TextField(
        blank=True, default="", verbose_name=_("Notas del comprador")
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True,
        verbose_name=_("Estado"),
    )

    # Los totales los calcula el backend: el frontend no impone precios.
    total_neto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Total neto"),
    )
    total_iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Total IVA (19%)"),
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Total general"),
    )

    # Las fechas las trae ModeloDeTienda: `fecha_creacion` y `fecha_edicion`.
    # Este modelo declaraba además `creado_en` y `actualizado_en`, así que la
    # tabla tenía cuatro columnas para dos cosas y cualquier consulta podía
    # tomar la equivocada sin fallar.

    class Meta(ModeloDeTienda.Meta):
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["tienda", "estado"]),
            models.Index(fields=["tienda", "fecha_creacion"]),
        ]

    def __str__(self):
        return f"{self.folio} - {self.nombre_contacto} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        if not self.folio:
            self.folio = f"DC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @transaction.atomic
    def anular(self):
        """
        Cancela el pedido y devuelve a cada producto lo que tenía reservado.

        La fila se bloquea para reponer: si el dueño anula mientras alguien
        está comprando, los dos leen y escriben el mismo stock y uno de los
        dos cambios se pierde.

        Anular dos veces no repone dos veces: se sale temprano si ya estaba
        cancelado.
        """
        if self.estado == self.Estado.CANCELADO:
            return

        for linea in self.lineas.all():
            producto = Producto.objects.select_for_update().get(pk=linea.producto_id)

            # Quien no lleva inventario no tiene nada que reponer: la tienda
            # no sabe cuánto le queda y el stock es nulo a propósito.
            if not producto.controla_stock:
                continue

            producto.stock += linea.cantidad
            producto.save(update_fields=["stock"])

        self.estado = self.Estado.CANCELADO
        self.save(update_fields=["estado", "fecha_edicion"])


class LineaPedido(models.Model):
    """
    Detalle de los productos adquiridos en el pedido.
    Guarda una copia de los precios y cantidades tal como estaban al
    confirmar el pedido.
    """

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="lineas",
        verbose_name=_("Pedido"),
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="lineas_pedido",
        verbose_name=_("Producto"),
    )
    # Decimales para lo que se vende por peso (gramos) y enteros para los
    # lotes y las unidades.
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Cantidad"),
    )
    precio_unitario_neto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Precio unitario neto"),
    )
    subtotal_neto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Subtotal neto"),
    )
    subtotal_iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Subtotal IVA"),
    )
    subtotal_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Subtotal total"),
    )

    class Meta:
        verbose_name = _("Línea de pedido")
        verbose_name_plural = _("Líneas de pedido")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en {self.pedido.folio}"
