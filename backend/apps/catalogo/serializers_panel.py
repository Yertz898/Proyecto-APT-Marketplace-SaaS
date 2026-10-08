"""
Serializadores del catálogo visto desde el panel.

No es el mismo contrato que la vitrina y por eso no se reutiliza: el panel
muestra lo que el comprador no ve —lo desactivado, lo agotado, el stock exacto—
y omite lo que al dueño no le hace falta, como el IVA de cada producto, que ya
sabe calcular.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.catalogo.models import Categoria, FormaVenta, Producto, UnidadMedida
from apps.core.medios import imagen
from apps.core.validadores import validar_imagen
from apps.precios.models import TramoPrecio, UnidadUmbral


class ProductoDelPanelSerializer(serializers.ModelSerializer):
    """
    Un producto como lo lista y lo edita el panel.

    Trae **todo lo editable**, no un resumen. Tentaba dejar fuera la
    descripción y las piezas porque la tabla no las muestra, pero entonces el
    formulario se abriría con esos campos vacíos y guardarlos los borraría.
    """

    formaVenta = serializers.CharField(source="forma_venta", read_only=True)
    unidadMedida = serializers.CharField(source="unidad_medida", read_only=True)
    categoria = serializers.CharField(
        source="categoria.nombre", read_only=True, default=None
    )
    precioNeto = serializers.IntegerField(source="precio_neto", read_only=True)
    controlaStock = serializers.BooleanField(source="controla_stock", read_only=True)
    stock = serializers.SerializerMethodField()
    cantidadMinima = serializers.SerializerMethodField()
    cantidadPiezas = serializers.IntegerField(
        source="cantidad_piezas", read_only=True, default=None
    )
    tramos = serializers.IntegerField(source="tramos.count", read_only=True)
    estado = serializers.SerializerMethodField()
    foto = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "categoria",
            "formaVenta",
            "unidadMedida",
            "precioNeto",
            "controlaStock",
            "stock",
            "cantidadMinima",
            "cantidadPiezas",
            "tramos",
            "activo",
            "estado",
            "foto",
        ]

    def get_stock(self, producto) -> float | int | None:
        return _numero(producto.stock)

    def get_cantidadMinima(self, producto) -> float | int | None:  # noqa: N802
        return _numero(producto.cantidad_minima)

    def get_foto(self, producto) -> dict | None:
        """
        La foto, para que el panel muestre cuál hay antes de reemplazarla.

        Null cuando no hay: la pantalla no dibuja un marcador gris, que se
        confunde con una foto que no cargó.
        """
        return imagen(producto.foto, producto.nombre)

    def get_estado(self, producto) -> str:
        """
        En una palabra, qué le pasa a este producto.

        Es lo que ordena la tabla del panel: primero lo que pide atención. Son
        hechos, no predicciones: la alerta por demanda proyectada necesita el
        pronóstico, que todavía no existe.
        """
        if not producto.activo:
            return "desactivado"
        if producto.agotado:
            return "agotado"
        if producto.controla_stock and producto.stock == 1:
            return "ultima"
        return "publicado"


class ResumenDeInventarioSerializer(serializers.Serializer):
    """Las cuatro cifras que el dueño mira primero."""

    publicados = serializers.IntegerField()
    desactivados = serializers.IntegerField()
    agotados = serializers.IntegerField()
    ultimaUnidad = serializers.IntegerField()


class EdicionDeProductoSerializer(serializers.ModelSerializer):
    """
    Crear y editar un producto desde el panel.

    La tienda no viaja en el cuerpo: la pone la vista desde el token. Mandarla
    no sirve de nada.

    La categoría va **por nombre** y no por identificador. Dos razones: el
    nombre es único dentro de la tienda, así que alcanza; y un identificador en
    el cuerpo sería una invitación a probar los de otra tienda.
    """

    categoria = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    formaVenta = serializers.ChoiceField(
        source="forma_venta", choices=FormaVenta.choices, required=False
    )
    unidadMedida = serializers.ChoiceField(
        source="unidad_medida", choices=UnidadMedida.choices, required=False
    )
    precioNeto = serializers.IntegerField(source="precio_neto", min_value=1)
    controlaStock = serializers.BooleanField(source="controla_stock", required=False)
    stock = serializers.DecimalField(
        max_digits=12, decimal_places=3, required=False, allow_null=True
    )
    cantidadMinima = serializers.DecimalField(
        source="cantidad_minima", max_digits=12, decimal_places=3, required=False
    )
    cantidadPiezas = serializers.IntegerField(
        source="cantidad_piezas", required=False, allow_null=True
    )
    foto = serializers.ImageField(
        required=False, allow_null=True, validators=[validar_imagen]
    )

    class Meta:
        model = Producto
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "categoria",
            "formaVenta",
            "unidadMedida",
            "precioNeto",
            "controlaStock",
            "stock",
            "cantidadMinima",
            "cantidadPiezas",
            "foto",
            "activo",
        ]

    def validate_codigo(self, codigo):
        """
        Único dentro de la tienda.

        Se comprueba acá además de en la base para responder 400 con el campo
        marcado, y no un 500 con un error de integridad.
        """
        codigo = codigo.strip()
        hermanos = Producto.objects.filter(tienda=self.context["tienda"], codigo=codigo)
        if self.instance:
            hermanos = hermanos.exclude(pk=self.instance.pk)

        if hermanos.exists():
            raise serializers.ValidationError(
                "Ya tienes un producto con este código.", code="codigo_repetido"
            )
        return codigo

    def validate_categoria(self, nombre):
        """La categoría tiene que ser de esta tienda. Se busca, no se crea."""
        if not nombre:
            return None

        try:
            return Categoria.objects.get(tienda=self.context["tienda"], nombre=nombre)
        except Categoria.DoesNotExist:
            raise serializers.ValidationError(
                "Esa categoría no existe en tu tienda.", code="categoria_desconocida"
            ) from None

    def validate(self, datos):
        """
        Las reglas cruzadas del modelo, antes de tocar la base.

        El modelo ya las tiene en `clean()` y la base en sus restricciones. Si
        no se llaman acá, una combinación inválida llega a PostgreSQL y vuelve
        como un 500 sin decir qué campo estaba mal.
        """
        producto = self.instance or Producto(tienda=self.context["tienda"])
        for campo, valor in datos.items():
            setattr(producto, campo, valor)

        try:
            producto.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(_detalles(error)) from error

        return datos

    def create(self, datos):
        return Producto.objects.create(tienda=self.context["tienda"], **datos)


def _detalles(error: DjangoValidationError) -> dict:
    """
    Los errores de Django con la forma que espera DRF, sin perder el código.

    `ErrorDetail` conserva el `code`, que es el contrato: el texto se puede
    reescribir, el código no.
    """
    if not hasattr(error, "error_dict"):
        return {
            "detail": [
                serializers.ErrorDetail(m, code="invalido") for m in error.messages
            ]
        }

    return {
        campo: [
            serializers.ErrorDetail(
                e.message % (e.params or {}), code=e.code or "invalido"
            )
            for e in errores
        ]
        for campo, errores in error.error_dict.items()
    }


class CategoriaSerializer(serializers.ModelSerializer):
    """
    Una categoría de la tienda.

    `tienda` no está entre los campos a propósito: la pone la vista desde el
    token. Que el cuerpo pudiera elegirla sería la fuga más barata del sistema.
    """

    productos = serializers.IntegerField(source="productos.count", read_only=True)

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "productos"]

    def validate_nombre(self, nombre):
        nombre = nombre.strip()
        hermanas = Categoria.objects.filter(
            tienda=self.context["request"].user.tienda, nombre=nombre
        )
        if self.instance:
            hermanas = hermanas.exclude(pk=self.instance.pk)

        if hermanas.exists():
            raise serializers.ValidationError(
                "Ya tienes una categoría con este nombre.", code="nombre_repetido"
            )
        return nombre


class TramoSerializer(serializers.ModelSerializer):
    """
    Un escalón de precio de un producto.

    `valor` es siempre un precio unitario neto. En DealCommerce no hay
    descuentos: si hace falta otro precio, es otro tramo.
    """

    unidadUmbral = serializers.ChoiceField(
        source="unidad_umbral", choices=UnidadUmbral.choices
    )
    precioNeto = serializers.IntegerField(source="valor", min_value=1)

    class Meta:
        model = TramoPrecio
        fields = ["id", "umbral", "unidadUmbral", "precioNeto"]

    def validate_umbral(self, umbral):
        if umbral < 0:
            raise serializers.ValidationError(
                "El umbral no puede ser negativo.", code="umbral_negativo"
            )
        return umbral

    def validate(self, datos):
        """
        Dos tramos con el mismo umbral y unidad se pisan.

        La base lo impide, pero un error de integridad vuelve como 500 y sin
        decir qué campo repetir.
        """
        if self.instance:
            producto = self.instance.producto
        else:
            producto = self.context.get("producto")
        if producto is None:
            return datos

        unidad = datos.get(
            "unidad_umbral", self.instance.unidad_umbral if self.instance else None
        )
        umbral = datos.get("umbral", self.instance.umbral if self.instance else None)

        hermanos = TramoPrecio.objects.filter(
            producto=producto, unidad_umbral=unidad, umbral=umbral
        )
        if self.instance:
            hermanos = hermanos.exclude(pk=self.instance.pk)

        if hermanos.exists():
            raise serializers.ValidationError(
                {"umbral": "Este producto ya tiene un tramo con ese umbral."},
                code="tramo_repetido",
            )

        return datos


def _numero(valor) -> float | int | None:
    """Entero cuando no tiene decimales. Evita los «10,000» en pantalla."""
    if valor is None:
        return None
    return int(valor) if valor == valor.to_integral_value() else float(valor)
