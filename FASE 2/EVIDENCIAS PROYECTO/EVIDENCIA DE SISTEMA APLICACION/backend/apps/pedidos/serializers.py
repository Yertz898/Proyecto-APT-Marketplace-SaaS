from decimal import Decimal
from rest_framework import serializers
from apps.pedidos.models import Pedido, LineaPedido
from apps.catalogo.models import Producto


class LineaPedidoInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))


class CheckoutSimuladoSerializer(serializers.Serializer):
    nombre_contacto = serializers.CharField(max_length=150)
    telefono_contacto = serializers.CharField(max_length=30)
    email_contacto = serializers.EmailField(required=False, allow_blank=True, default='')
    direccion_entrega = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    notas = serializers.CharField(required=False, allow_blank=True, default='')
    lineas = LineaPedidoInputSerializer(many=True, allow_empty=False)


class LineaPedidoDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)

    class Meta:
        model = LineaPedido
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'producto_codigo',
            'cantidad',
            'precio_unitario_neto',
            'subtotal_neto',
            'subtotal_iva',
            'subtotal_total',
        ]


class PedidoDetalleSerializer(serializers.ModelSerializer):
    lineas = LineaPedidoDetalleSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id',
            'folio',
            'estado',
            'estado_display',
            'nombre_contacto',
            'telefono_contacto',
            'email_contacto',
            'direccion_entrega',
            'notas',
            'total_neto',
            'total_iva',
            'total',
            'creado_en',
            'lineas',
        ]