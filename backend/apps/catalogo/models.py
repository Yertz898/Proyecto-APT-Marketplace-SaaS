"""
Catálogo: lotes y líneas de granel.

Son las dos formas de vender, y no se parecen entre sí:

- Un **lote** es una unidad cerrada que se compra entera. Lo que se cuenta no
  es stock de piezas sino cupos: cuántas veces más se puede vender ese lote.
  Un lote de cupo único se vende una sola vez.
- Una **línea de granel** se vende por gramo. No tiene stock, porque el cliente
  no registra gramos: lleva un interruptor de disponibilidad que el dueño
  maneja a mano.

Un lote no es una lista de piezas concretas: es una composición, cuántas piezas
de cada categoría, porque los modelos varían según lo que le llega al cliente.
La suma de esa composición tiene que cuadrar con la cantidad de piezas del
lote, y eso se valida al guardar.

Acá no hay productos ni variantes.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.managers import ManagerDeTienda, QuerySetDeTienda
from apps.core.models import ModeloDeTienda


class Categoria(ModeloDeTienda):
    """
    Anillos, aros, cadenas… Las define cada tienda, no la plataforma.

    Un lote declara cuántas piezas trae de cada una, y una línea de granel dice
    cuáles abarca.
    """

    nombre = models.CharField("nombre", max_length=60)

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["tienda", "nombre"], name="catalogo_categoria_unica_por_tienda"
            ),
        ]

    def __str__(self):
        return self.nombre


class TipoCupo(models.TextChoices):
    UNICO = "UNICO", "Cupo único"
    MULTIPLE = "MULTIPLE", "Cupos múltiples"


class QuerySetDeLotes(QuerySetDeTienda):
    def publicadas_de(self, tienda):
        """
        Lo que ve la vitrina: activo y con cupos.

        Un lote agotado o desactivado no se muestra ni se puede pedir por su
        código: para el comprador no existe.
        """
        return self.filter(tienda=tienda, activo=True, cupos_disponibles__gt=0)


class Lote(ModeloDeTienda):
    """Unidad de venta cerrada. Se compra entera, sin elegir piezas."""

    codigo = models.CharField("código", max_length=40)
    nombre = models.CharField("nombre", max_length=150)
    material = models.CharField("material predominante", max_length=60)

    cantidad_piezas = models.PositiveIntegerField("cantidad de piezas")

    # Pesos chilenos enteros y netos. El IVA se calcula aparte al mostrarlo.
    precio_neto = models.PositiveIntegerField("precio neto")

    tipo_cupo = models.CharField(
        "tipo de cupo",
        max_length=10,
        choices=TipoCupo.choices,
        default=TipoCupo.MULTIPLE,
    )
    cupos_totales = models.PositiveIntegerField("cupos totales", default=1)
    cupos_disponibles = models.PositiveIntegerField("cupos disponibles", default=1)

    # varchar(255) en el diccionario: la base guarda la clave del objeto, nunca
    # la URL completa. ImageField almacena exactamente eso y además valida que
    # el archivo sea una imagen.
    foto = models.ImageField(
        "foto", upload_to="lotes/", max_length=255, blank=True, null=True
    )
    activo = models.BooleanField("activo", default=True)

    objects = ManagerDeTienda.from_queryset(QuerySetDeLotes)()

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "lote"
        verbose_name_plural = "lotes"
        ordering = ["codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["tienda", "codigo"],
                name="catalogo_lote_codigo_unico_por_tienda",
            ),
            # La base de datos sostiene el invariante de los cupos: una vista
            # mal escrita no puede dejar un lote con más vendidos que totales.
            models.CheckConstraint(
                condition=models.Q(cupos_disponibles__lte=models.F("cupos_totales")),
                name="catalogo_lote_cupos_dentro_del_total",
            ),
            models.CheckConstraint(
                condition=models.Q(cupos_totales__gt=0),
                name="catalogo_lote_cupos_totales_positivos",
            ),
            # Un lote de cupo único es, por definición, uno solo.
            models.CheckConstraint(
                condition=(
                    ~models.Q(tipo_cupo=TipoCupo.UNICO) | models.Q(cupos_totales=1)
                ),
                name="catalogo_lote_cupo_unico_es_uno",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad_piezas__gt=0),
                name="catalogo_lote_piezas_positivas",
            ),
        ]
        indexes = [models.Index(fields=["tienda", "activo"])]

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"

    @property
    def agotado(self) -> bool:
        return self.cupos_disponibles == 0

    def clean(self):
        super().clean()
        if self.tipo_cupo == TipoCupo.UNICO and self.cupos_totales != 1:
            raise ValidationError(
                {
                    "cupos_totales": ValidationError(
                        "Un lote de cupo único tiene un solo cupo.",
                        code="cupo_unico_es_uno",
                    )
                }
            )
        if self.cupos_disponibles > self.cupos_totales:
            raise ValidationError(
                {
                    "cupos_disponibles": ValidationError(
                        "No puede haber más cupos libres que totales.",
                        code="cupos_fuera_de_rango",
                    )
                }
            )
        self.validar_composicion()

    def validar_composicion(self):
        """
        La composición tiene que sumar exactamente la cantidad de piezas.

        Se valida solo cuando ya hay composición cargada: un lote recién creado
        todavía no tiene filas, y exigirlas ahí impediría crearlo.
        """
        if not self.pk:
            return

        piezas = self.composicion.aggregate(total=models.Sum("cantidad"))["total"]
        if piezas is None:
            return

        if piezas != self.cantidad_piezas:
            raise ValidationError(
                {
                    "cantidad_piezas": ValidationError(
                        f"La composición suma {piezas} piezas y el lote declara "
                        f"{self.cantidad_piezas}.",
                        code="composicion_no_cuadra",
                    )
                }
            )


class ComposicionLote(ModeloDeTienda):
    """
    Cuántas piezas de cada categoría trae un lote.

    No es una lista de piezas concretas: los modelos varían según lo que le
    llega al cliente, así que lo que se promete es la mezcla, no el detalle.
    """

    lote = models.ForeignKey(
        Lote, verbose_name="lote", on_delete=models.CASCADE, related_name="composicion"
    )
    categoria = models.ForeignKey(
        Categoria,
        verbose_name="categoría",
        on_delete=models.PROTECT,
        related_name="composiciones",
    )
    cantidad = models.PositiveIntegerField("cantidad de piezas")

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "composición del lote"
        verbose_name_plural = "composiciones de lote"
        ordering = ["categoria__nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "categoria"],
                name="catalogo_composicion_categoria_unica_por_lote",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="catalogo_composicion_cantidad_positiva",
            ),
        ]

    def __str__(self):
        return f"{self.cantidad} × {self.categoria}"

    def clean(self):
        super().clean()
        # Una categoría de otra tienda dentro de un lote sería una fuga de
        # datos por la puerta de atrás: el nombre de la categoría ajena
        # quedaría visible en la vitrina.
        if self.lote_id and self.categoria_id:
            if self.categoria.tienda_id != self.lote.tienda_id:
                raise ValidationError(
                    {
                        "categoria": ValidationError(
                            "La categoría es de otra tienda.",
                            code="categoria_de_otra_tienda",
                        )
                    }
                )


class QuerySetDeGranel(QuerySetDeTienda):
    def publicadas_de(self, tienda):
        """La vitrina solo muestra las líneas que el dueño dejó disponibles."""
        return self.filter(tienda=tienda, disponible=True)


class LineaGranel(ModeloDeTienda):
    """
    Venta por gramo.

    No tiene stock: el cliente no registra gramos, así que lo único que decide
    si se puede comprar es el interruptor `disponible`, que el dueño maneja a
    mano.
    """

    codigo = models.CharField("código", max_length=40)
    nombre = models.CharField("nombre", max_length=150)
    material = models.CharField("material", max_length=60)

    # Texto y no relación, como lo fija el diccionario: acá las categorías son
    # descriptivas ("cadenas, pulseras"), no estructurales como en la
    # composición de un lote.
    categorias = models.CharField(
        "categorías que abarca",
        max_length=200,
        blank=True,
        help_text="Separadas por coma. Ej.: cadenas, pulseras.",
    )

    disponible = models.BooleanField("disponible", default=True)

    foto = models.ImageField(
        "foto de referencia", upload_to="granel/", max_length=255, blank=True, null=True
    )

    objects = ManagerDeTienda.from_queryset(QuerySetDeGranel)()

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "línea de granel"
        verbose_name_plural = "líneas de granel"
        ordering = ["codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["tienda", "codigo"],
                name="catalogo_granel_codigo_unico_por_tienda",
            ),
        ]

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"
