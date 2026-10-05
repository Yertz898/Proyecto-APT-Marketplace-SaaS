"""
Serializadores del catálogo visto desde el panel.

No es el mismo contrato que la vitrina y por eso no se reutiliza: el panel
muestra lo que el comprador no ve —lo desactivado, lo agotado, el stock exacto—
y omite lo que al dueño no le hace falta, como el IVA de cada producto, que ya
sabe calcular.
"""

from rest_framework import serializers

from apps.catalogo.models import Producto


class ProductoDelPanelSerializer(serializers.ModelSerializer):
    formaVenta = serializers.CharField(source="forma_venta", read_only=True)
    unidadMedida = serializers.CharField(source="unidad_medida", read_only=True)
    categoria = serializers.CharField(
        source="categoria.nombre", read_only=True, default=None
    )
    precioNeto = serializers.IntegerField(source="precio_neto", read_only=True)
    controlaStock = serializers.BooleanField(source="controla_stock", read_only=True)
    stock = serializers.SerializerMethodField()
    tramos = serializers.IntegerField(source="tramos.count", read_only=True)
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "codigo",
            "nombre",
            "categoria",
            "formaVenta",
            "unidadMedida",
            "precioNeto",
            "controlaStock",
            "stock",
            "tramos",
            "activo",
            "estado",
        ]

    def get_stock(self, producto) -> float | int | None:
        if producto.stock is None:
            return None
        entero = producto.stock == producto.stock.to_integral_value()
        return int(producto.stock) if entero else float(producto.stock)

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
