"""
Serializadores del catálogo público.

Un solo serializador para todas las formas de venta. Los campos que no aplican
a una forma viajan en `null`, no en otra forma: así el frontend tiene un tipo y
no tres, y una tienda que mañana venda de otra manera no obliga a tocar esto.

Las claves compuestas van en camelCase porque este contrato lo consume el
frontend, y el IVA y el total vienen calculados: el navegador no hace
aritmética de dinero.
"""

from rest_framework import serializers

from apps.catalogo.models import FormaVenta, Producto
from apps.core.medios import imagen
from apps.precios.dinero import desglose
from apps.precios.models import UnidadUmbral

#: En qué unidad se miden los umbrales directos de cada forma de venta.
#: Los de monto se leen aparte, porque valen para todas.
UNIDAD_NATURAL = {
    FormaVenta.UNIDAD: UnidadUmbral.CANTIDAD,
    FormaVenta.LOTE: UnidadUmbral.CANTIDAD,
    FormaVenta.PESO: UnidadUmbral.PESO,
}


class ComposicionSerializer(serializers.Serializer):
    """Cuántas piezas de cada categoría. No es una lista de piezas concretas."""

    categoria = serializers.CharField(source="categoria.nombre", read_only=True)
    cantidad = serializers.IntegerField(read_only=True)


class TramoSerializer(serializers.Serializer):
    umbral = serializers.SerializerMethodField()
    unidadUmbral = serializers.CharField(source="unidad_umbral", read_only=True)
    precioNeto = serializers.IntegerField(source="valor", read_only=True)

    def get_umbral(self, tramo) -> float | int:
        """Entero cuando no tiene decimales, para que la vitrina no muestre «500,00»."""
        umbral = tramo.umbral
        return int(umbral) if umbral == umbral.to_integral_value() else float(umbral)


class ProductoSerializer(serializers.ModelSerializer):
    formaVenta = serializers.CharField(source="forma_venta", read_only=True)
    unidadMedida = serializers.CharField(source="unidad_medida", read_only=True)
    categoria = serializers.CharField(
        source="categoria.nombre", read_only=True, default=None
    )

    precioNeto = serializers.IntegerField(source="precio_neto", read_only=True)
    iva = serializers.SerializerMethodField()
    precioTotal = serializers.SerializerMethodField()

    disponibilidad = serializers.SerializerMethodField()
    agotado = serializers.ReadOnlyField()

    cantidadMinima = serializers.SerializerMethodField()
    piezasTotales = serializers.IntegerField(
        source="cantidad_piezas", read_only=True, default=None
    )
    composicion = ComposicionSerializer(many=True, read_only=True)

    tramos = serializers.SerializerMethodField()
    minimo = serializers.SerializerMethodField()
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
            "iva",
            "precioTotal",
            "disponibilidad",
            "agotado",
            "cantidadMinima",
            "piezasTotales",
            "composicion",
            "tramos",
            "minimo",
            "foto",
        ]

    def get_iva(self, producto) -> int:
        return desglose(producto.precio_neto)["iva"]

    def get_precioTotal(self, producto) -> int:  # noqa: N802 — lo fija el contrato
        return desglose(producto.precio_neto)["total"]

    def get_cantidadMinima(self, producto) -> float | int:  # noqa: N802
        return _numero(producto.cantidad_minima)

    def get_disponibilidad(self, producto) -> dict:
        """
        Qué se le puede decir al comprador sobre las existencias.

        Son tres situaciones distintas y conviene que el frontend no tenga que
        deducirlas: la tienda no lleva inventario de esto, queda una sola
        unidad, o quedan varias. La última unidad se dice aparte porque empuja
        a decidir, y «queda 1» en algo que por definición es único no aporta.
        """
        if not producto.controla_stock:
            return {"tipo": "sin_control"}
        if producto.agotado:
            return {"tipo": "agotado"}
        if producto.stock == 1:
            return {"tipo": "ultima"}
        return {"tipo": "disponible", "restantes": _numero(producto.stock)}

    def get_tramos(self, producto) -> list[dict]:
        """
        Ordenados como los lee una persona: primero los de monto, después los
        de la unidad del producto, y dentro de cada grupo de menor a mayor.
        """
        natural = UNIDAD_NATURAL[FormaVenta(producto.forma_venta)]
        tramos = sorted(
            producto.tramos.all(),
            key=lambda t: (t.unidad_umbral == natural, t.umbral),
        )
        return TramoSerializer(tramos, many=True).data

    def get_minimo(self, producto) -> str | None:
        """
        El mínimo de compra por monto, redactado acá y no en el navegador.

        Sale del tramo por monto más bajo: bajo ese monto de referencia la
        compra se rechaza. No es lo mismo que `cantidadMinima`, que cuenta
        unidades o gramos.
        """
        por_monto = [
            t for t in producto.tramos.all() if t.unidad_umbral == UnidadUmbral.MONTO
        ]
        if not por_monto:
            return None

        minimo = min(int(t.umbral) for t in por_monto)
        return f"Compra mínima de ${minimo:,.0f}".replace(",", ".")

    def get_foto(self, producto) -> dict | None:
        """
        Null mientras no haya foto: la interfaz no dibuja nada en su lugar.

        Un marcador gris se confunde con una foto que no cargó.
        """
        return imagen(producto.foto, producto.nombre)


class CotizacionSerializer(serializers.Serializer):
    """
    Lo que cuesta una cantidad. Lo arma `apps.precios.servicios`.

    Un rechazo no es un error de la petición: la cantidad es válida y la
    respuesta es «no se puede, por esto». Por eso va con 200 y con el motivo
    adentro, para que la vitrina lo muestre donde corresponde.
    """

    cantidad = serializers.SerializerMethodField()
    precioUnitario = serializers.IntegerField(source="precio_unitario")
    neto = serializers.IntegerField()
    iva = serializers.IntegerField()
    total = serializers.IntegerField()
    tramoAplicado = serializers.SerializerMethodField()
    unidadTramo = serializers.CharField(source="unidad_tramo", allow_null=True)
    aviso = serializers.CharField(allow_null=True)
    rechazo = serializers.CharField(allow_null=True)
    motivo = serializers.CharField(allow_null=True)

    def get_cantidad(self, cotizacion) -> float | int:
        return _numero(cotizacion.cantidad)

    def get_tramoAplicado(self, cotizacion) -> float | int | None:  # noqa: N802
        if cotizacion.tramo_aplicado is None:
            return None
        return _numero(cotizacion.tramo_aplicado)


def _numero(valor) -> float | int:
    """Entero cuando no tiene decimales. Evita los «500,000» en pantalla."""
    if valor is None:
        return 0
    return int(valor) if valor == valor.to_integral_value() else float(valor)
