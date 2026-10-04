"""
Precios por tramos, para lotes y para granel.

Es el módulo con más lógica de negocio del sistema, y el que más fácil se
calcula mal.

En el granel los umbrales en gramos (medio kilo, kilo) tienen prioridad. Si la
cantidad no alcanza ninguno, se arma un monto de referencia con el precio del
primer tramo y se aplica el tramo en pesos que ese monto alcance. Bajo $20.000
de referencia la compra se rechaza. Los umbrales son inclusivos.

Dos reglas que no son de estilo:

- Los precios se guardan netos. El IVA (19%) se calcula aparte y se muestra
  separado del neto y del total.
- El cálculo va con `Decimal` y `ROUND_HALF_UP`. El `round()` de Python
  redondea al par más cercano y deja el total un peso corto en casos como
  3.828,50.

Los tramos por cantidad de lotes todavía no los dijo el cliente: quedan
configurables por tienda, nunca escritos en el código.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import ModeloDeTienda


class UnidadUmbral(models.TextChoices):
    PESOS = "pesos", "Pesos"
    GRAMOS = "gramos", "Gramos"
    LOTES = "lotes", "Cantidad de lotes"


class TramoPrecio(ModeloDeTienda):
    """
    Un escalón de precio: desde tal umbral, este precio por unidad.

    Sirve a los dos casos y por eso `linea_granel` puede ir vacío:

    - Con línea, es un tramo del granel de esa línea, y el precio es por gramo.
    - Sin línea, es un tramo por cantidad de lotes de toda la tienda. Esos no
      los ha definido el cliente, así que la tienda parte sin ninguno.
    """

    linea_granel = models.ForeignKey(
        "catalogo.LineaGranel",
        verbose_name="línea de granel",
        on_delete=models.CASCADE,
        related_name="tramos",
        blank=True,
        null=True,
    )

    unidad_umbral = models.CharField(
        "unidad del umbral", max_length=10, choices=UnidadUmbral.choices
    )

    # Decimal y no Float: un umbral en gramos admite decimales y el dinero no
    # tolera el error de coma flotante.
    umbral = models.DecimalField("umbral", max_digits=12, decimal_places=2)

    # El diccionario lo llama `valor` porque significa dos cosas según el
    # destino: en el granel es el precio por gramo neto, y en los tramos por
    # cantidad de lotes es un porcentaje de descuento.
    valor = models.PositiveIntegerField("precio por gramo neto o % de descuento")

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "tramo de precio"
        verbose_name_plural = "tramos de precio"
        ordering = ["linea_granel", "unidad_umbral", "umbral"]
        constraints = [
            # Dos tramos con el mismo umbral y la misma unidad se pisan: el
            # motor no sabría cuál aplicar.
            models.UniqueConstraint(
                fields=["linea_granel", "unidad_umbral", "umbral"],
                condition=models.Q(linea_granel__isnull=False),
                name="precios_tramo_unico_por_linea",
            ),
            models.UniqueConstraint(
                fields=["tienda", "unidad_umbral", "umbral"],
                condition=models.Q(linea_granel__isnull=True),
                name="precios_tramo_unico_por_tienda",
            ),
            models.CheckConstraint(
                condition=models.Q(umbral__gte=0),
                name="precios_umbral_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(valor__gt=0),
                name="precios_precio_positivo",
            ),
            # Un tramo de una línea se mide en pesos o gramos; uno por cantidad
            # de lotes no cuelga de ninguna línea.
            models.CheckConstraint(
                condition=(
                    models.Q(linea_granel__isnull=False)
                    & models.Q(
                        unidad_umbral__in=[UnidadUmbral.PESOS, UnidadUmbral.GRAMOS]
                    )
                )
                | (
                    models.Q(linea_granel__isnull=True)
                    & models.Q(unidad_umbral=UnidadUmbral.LOTES)
                ),
                name="precios_unidad_segun_destino",
            ),
        ]

    def __str__(self):
        destino = self.linea_granel.codigo if self.linea_granel_id else "lotes"
        return f"{destino}: desde {self.umbral} {self.unidad_umbral}"

    def clean(self):
        super().clean()
        if self.linea_granel_id and self.linea_granel.tienda_id != self.tienda_id:
            raise ValidationError(
                {
                    "linea_granel": ValidationError(
                        "La línea de granel es de otra tienda.",
                        code="linea_de_otra_tienda",
                    )
                }
            )
