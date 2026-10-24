"""
Precios por tramos.

Es el módulo con más lógica de negocio del sistema, y el que más fácil se
calcula mal.

Un tramo dice «desde tal cantidad, este precio por unidad». **Siempre cuelga de
un producto y su valor es siempre un precio unitario neto**: en DealCommerce no
hay descuentos ni porcentajes. Si algo parece pedir un porcentaje, lo que
corresponde es otro tramo.

Los umbrales en peso o en cantidad tienen prioridad. Si lo pedido no alcanza
ninguno, se arma un monto de referencia con el precio del producto y se aplica
el tramo por monto que ese monto alcance. Si no llega ni al primero, se
rechaza. Los umbrales son inclusivos.

Dos reglas que no son de estilo:

- Los precios se guardan netos. El IVA (19%) se calcula aparte y se muestra
  separado del neto y del total.
- El cálculo va con `Decimal` y `ROUND_HALF_UP`. El `round()` de Python
  redondea al par más cercano y deja el total un peso corto en casos como
  3.828,50.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import ModeloDeTienda


class UnidadUmbral(models.TextChoices):
    CANTIDAD = "cantidad", "Cantidad"
    MONTO = "monto", "Monto"
    PESO = "peso", "Peso"


class TramoPrecio(ModeloDeTienda):
    """
    Un escalón de precio: desde tal umbral, este precio por unidad de medida.

    El producto es obligatorio: no existen tramos de toda la tienda. Un precio
    por volumen es del producto que se vende, y dejar que colgara de la tienda
    abría la puerta a mezclarlo con descuentos, que acá no existen.
    """

    producto = models.ForeignKey(
        "catalogo.Producto",
        verbose_name="producto",
        on_delete=models.CASCADE,
        related_name="tramos",
    )

    unidad_umbral = models.CharField(
        "unidad del umbral", max_length=10, choices=UnidadUmbral.choices
    )

    # Decimal y no Float: un umbral en peso admite decimales y el dinero no
    # tolera el error de coma flotante.
    umbral = models.DecimalField("umbral", max_digits=12, decimal_places=2)

    # Precio neto por unidad de medida del producto: por unidad, por lote o por
    # gramo, según cómo se venda.
    valor = models.PositiveIntegerField("precio unitario neto")

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "tramo de precio"
        verbose_name_plural = "tramos de precio"
        ordering = ["producto", "unidad_umbral", "umbral"]
        constraints = [
            # Dos tramos con el mismo umbral y la misma unidad se pisan: el
            # motor no sabría cuál aplicar.
            models.UniqueConstraint(
                fields=["tienda", "producto", "unidad_umbral", "umbral"],
                name="precios_tramo_unico",
            ),
            models.CheckConstraint(
                condition=models.Q(umbral__gte=0),
                name="precios_umbral_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(valor__gt=0),
                name="precios_precio_positivo",
            ),
        ]

    def __str__(self):
        return f"{self.producto.codigo}: desde {self.umbral} {self.unidad_umbral}"

    def clean(self):
        super().clean()
        if self.producto_id and self.producto.tienda_id != self.tienda_id:
            raise ValidationError(
                {
                    "producto": ValidationError(
                        "El producto es de otra tienda.",
                        code="producto_de_otra_tienda",
                    )
                }
            )
