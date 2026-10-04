"""
Catálogo: un solo producto que sirve a cualquier rubro.

DealCommerce es una plataforma, no la tienda de un cliente. Una tienda de ropa
vende por unidad y lleva inventario; una joyería vende lotes cerrados y vende
por gramo sin registrar lo que le queda. Las dos caben en el mismo modelo:

- `forma_venta` dice cómo se vende —por unidad, por lote o por peso—.
- `controla_stock` dice si la tienda lleva inventario de ese producto.

Los **cupos no son un concepto aparte**: son el stock de un producto vendido
por lote, y un lote que se vende una sola vez es un producto con `stock = 1`.
Así descontar inventario es una sola lógica para todas las tiendas, en vez de
dos que hay que recordar mantener iguales.

Un producto vendido por lote no es una lista de piezas concretas: es una
composición —cuántas piezas de cada categoría—, porque los modelos varían según
lo que le llega a la tienda. La suma tiene que cuadrar con `cantidad_piezas`, y
eso se valida al guardar.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.managers import ManagerDeTienda, QuerySetDeTienda
from apps.core.models import ModeloDeTienda


class Categoria(ModeloDeTienda):
    """
    Las define cada tienda, no la plataforma.

    Las usan el catálogo, la composición de los productos vendidos por lote y
    el pronóstico de demanda.
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


class FormaVenta(models.TextChoices):
    UNIDAD = "unidad", "Por unidad"
    LOTE = "lote", "Por lote"
    PESO = "peso", "Por peso"


class UnidadMedida(models.TextChoices):
    UNIDAD = "unidad", "Unidad"
    GRAMO = "g", "Gramo"
    KILO = "kg", "Kilo"


#: Unidades válidas para cada forma de venta.
#:
#: Vendido por peso se mide en gramos o kilos; por unidad y por lote, la unidad
#: es la pieza o el lote entero. La misma regla está como restricción en la base.
UNIDADES_POR_FORMA = {
    FormaVenta.UNIDAD: [UnidadMedida.UNIDAD],
    FormaVenta.LOTE: [UnidadMedida.UNIDAD],
    FormaVenta.PESO: [UnidadMedida.GRAMO, UnidadMedida.KILO],
}


class QuerySetDeProductos(QuerySetDeTienda):
    def publicadas_de(self, tienda):
        """
        Lo que ve la vitrina: activo y, si lleva inventario, con existencias.

        Un producto agotado o desactivado no se muestra ni se puede pedir por
        su código: para el comprador no existe. El que no controla stock se
        muestra mientras esté activo, porque la tienda no sabe cuánto le queda.
        """
        return self.filter(tienda=tienda, activo=True).exclude(
            controla_stock=True, stock__lte=0
        )

    def de_forma(self, forma):
        return self.filter(forma_venta=forma)


class Producto(ModeloDeTienda):
    """Lo que una tienda vende, sea cual sea su forma de venderlo."""

    codigo = models.CharField("código", max_length=40)
    nombre = models.CharField("nombre", max_length=150)
    descripcion = models.TextField("descripción", blank=True)

    # PROTECT y no CASCADE: borrar una categoría no puede llevarse productos
    # por delante. Opcional porque una tienda puede partir sin categorías.
    categoria = models.ForeignKey(
        Categoria,
        verbose_name="categoría",
        on_delete=models.PROTECT,
        related_name="productos",
        blank=True,
        null=True,
    )

    # Pesos chilenos enteros y netos, por unidad de medida. El IVA se calcula
    # aparte al mostrarlo. Es también el precio con que se arma el monto de
    # referencia de los tramos.
    precio_neto = models.PositiveIntegerField("precio neto")

    # varchar(255) en el diccionario: la base guarda la clave del objeto, nunca
    # la URL completa. ImageField almacena exactamente eso y además valida que
    # el archivo sea una imagen.
    foto = models.ImageField(
        "foto", upload_to="productos/", max_length=255, blank=True, null=True
    )
    activo = models.BooleanField("activo", default=True)

    forma_venta = models.CharField(
        "forma de venta",
        max_length=10,
        choices=FormaVenta.choices,
        default=FormaVenta.UNIDAD,
    )
    unidad_medida = models.CharField(
        "unidad de medida",
        max_length=10,
        choices=UnidadMedida.choices,
        default=UnidadMedida.UNIDAD,
    )

    controla_stock = models.BooleanField(
        "controla stock",
        default=True,
        help_text="Desactívalo si la tienda no lleva inventario de este producto.",
    )
    # Decimal y no Integer: un producto por peso se cuenta en gramos con
    # decimales. Nulo cuando no se controla, para que «no sé cuánto queda» no
    # se confunda con «no queda nada».
    stock = models.DecimalField(
        "stock", max_digits=12, decimal_places=3, blank=True, null=True
    )

    cantidad_minima = models.DecimalField(
        "cantidad mínima de compra",
        max_digits=12,
        decimal_places=3,
        default=Decimal("1"),
    )

    # Solo para la forma de venta por lote: contra esto cuadra la composición.
    cantidad_piezas = models.PositiveIntegerField(
        "cantidad de piezas", blank=True, null=True
    )

    objects = ManagerDeTienda.from_queryset(QuerySetDeProductos)()

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["tienda", "codigo"],
                name="catalogo_producto_codigo_unico_por_tienda",
            ),
            # El invariante del inventario lo sostiene la base: una vista mal
            # escrita no puede dejar un stock negativo ni un producto que dice
            # controlar inventario sin saber cuánto tiene.
            models.CheckConstraint(
                condition=(
                    models.Q(controla_stock=True, stock__isnull=False, stock__gte=0)
                    | models.Q(controla_stock=False, stock__isnull=True)
                ),
                name="catalogo_producto_stock_segun_control",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(forma_venta=FormaVenta.LOTE)
                    | models.Q(cantidad_piezas__isnull=True)
                ),
                name="catalogo_producto_piezas_solo_en_lote",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        forma_venta=FormaVenta.PESO,
                        unidad_medida__in=[UnidadMedida.GRAMO, UnidadMedida.KILO],
                    )
                    | models.Q(
                        forma_venta__in=[FormaVenta.UNIDAD, FormaVenta.LOTE],
                        unidad_medida=UnidadMedida.UNIDAD,
                    )
                ),
                name="catalogo_producto_unidad_segun_forma",
            ),
            models.CheckConstraint(
                condition=models.Q(precio_neto__gt=0),
                name="catalogo_producto_precio_positivo",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad_minima__gt=0),
                name="catalogo_producto_cantidad_minima_positiva",
            ),
        ]
        indexes = [
            models.Index(fields=["tienda", "activo"]),
            models.Index(fields=["tienda", "forma_venta"]),
        ]

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"

    @property
    def agotado(self) -> bool:
        """Sin existencias. El que no controla stock nunca está agotado."""
        return bool(self.controla_stock and (self.stock or 0) <= 0)

    def clean(self):
        super().clean()

        errores = {}

        if self.controla_stock and self.stock is None:
            errores["stock"] = ValidationError(
                "Si el producto controla stock, hay que decir cuánto hay.",
                code="stock_requerido",
            )
        if not self.controla_stock and self.stock is not None:
            errores["stock"] = ValidationError(
                "Este producto no controla stock, así que no lleva cantidad.",
                code="stock_no_corresponde",
            )
        if self.stock is not None and self.stock < 0:
            errores["stock"] = ValidationError(
                "El stock no puede ser negativo.", code="stock_negativo"
            )

        if self.unidad_medida not in UNIDADES_POR_FORMA[FormaVenta(self.forma_venta)]:
            errores["unidad_medida"] = ValidationError(
                "Esta unidad no corresponde a la forma de venta.",
                code="unidad_no_corresponde",
            )

        if self.forma_venta != FormaVenta.LOTE and self.cantidad_piezas is not None:
            errores["cantidad_piezas"] = ValidationError(
                "Solo un producto vendido por lote declara piezas.",
                code="piezas_solo_en_lote",
            )

        if errores:
            raise ValidationError(errores)

        self.validar_composicion()

    def validar_composicion(self):
        """
        La composición tiene que sumar exactamente la cantidad de piezas.

        Se valida solo cuando ya hay composición cargada: un producto recién
        creado todavía no tiene filas, y exigirlas ahí impediría crearlo.
        """
        if not self.pk or self.forma_venta != FormaVenta.LOTE:
            return

        piezas = self.composicion.aggregate(total=models.Sum("cantidad"))["total"]
        if piezas is None:
            return

        if piezas != self.cantidad_piezas:
            raise ValidationError(
                {
                    "cantidad_piezas": ValidationError(
                        f"La composición suma {piezas} piezas y el producto declara "
                        f"{self.cantidad_piezas}.",
                        code="composicion_no_cuadra",
                    )
                }
            )


class ComposicionLote(ModeloDeTienda):
    """
    Cuántas piezas de cada categoría trae un producto vendido por lote.

    No es una lista de piezas concretas: los modelos varían según lo que le
    llega a la tienda, así que lo que se promete es la mezcla, no el detalle.
    """

    producto = models.ForeignKey(
        Producto,
        verbose_name="producto",
        on_delete=models.CASCADE,
        related_name="composicion",
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
                fields=["producto", "categoria"],
                name="catalogo_composicion_categoria_unica_por_producto",
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

        if not (self.producto_id and self.categoria_id):
            return

        # Una categoría de otra tienda dentro de un producto sería una fuga de
        # datos por la puerta de atrás: el nombre de la categoría ajena
        # quedaría visible en la vitrina.
        if self.categoria.tienda_id != self.producto.tienda_id:
            raise ValidationError(
                {
                    "categoria": ValidationError(
                        "La categoría es de otra tienda.",
                        code="categoria_de_otra_tienda",
                    )
                }
            )

        if self.producto.forma_venta != FormaVenta.LOTE:
            raise ValidationError(
                {
                    "producto": ValidationError(
                        "Solo un producto vendido por lote tiene composición.",
                        code="composicion_solo_en_lote",
                    )
                }
            )
