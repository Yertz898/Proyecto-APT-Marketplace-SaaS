"""
Lo que entra y lo que sale de la API de pedidos.

La entrada del carrito identifica el producto por su **código**, que es como
lo nombra la tienda y lo que viaja en la URL de la vitrina. No por su id: un
número correlativo le dice a cualquiera cuántos productos hay en la
plataforma, y se puede recorrer.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.pedidos.models import LineaPedido, Pedido


class LineaDelCarritoSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=40)
    cantidad = serializers.DecimalField(
        max_digits=12, decimal_places=3, min_value=Decimal("0.001")
    )


class CheckoutSerializer(serializers.Serializer):
    """
    Con qué datos se cierra un pedido.

    El nombre y el teléfono son obligatorios aunque el comprador tenga cuenta:
    el pago y la entrega se coordinan por WhatsApp, y un pedido sin forma de
    contactar a quien lo hizo no se puede cerrar. Antes se tomaban del usuario
    autenticado, así que un invitado quedaba guardado como «Cliente Vitrina».
    """

    nombre_contacto = serializers.CharField(max_length=150)
    telefono_contacto = serializers.CharField(max_length=30)
    email_contacto = serializers.EmailField(
        required=False, allow_blank=True, default=""
    )
    direccion_entrega = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    notas = serializers.CharField(required=False, allow_blank=True, default="")
    rut_contacto = serializers.CharField(
        max_length=12, required=False, allow_blank=True, default=""
    )
    lineas = LineaDelCarritoSerializer(many=True, allow_empty=False)

    def validate(self, datos):
        """
        Quien compra sin cuenta deja su RUT, su nombre y su correo.

        Con cuenta, esos datos ya están en ella. Sin cuenta, son lo único que
        identifica al comprador ante la tienda: el RUT para la boleta y el
        correo para avisarle. Por eso se exigen acá y no en el navegador, que
        solo ayuda a llenarlos.
        """
        from apps.usuarios.validadores import normalizar_rut, validar_rut

        peticion = self.context.get("request")
        con_cuenta = bool(peticion and peticion.user.is_authenticated)
        errores = {}

        if datos.get("rut_contacto"):
            try:
                validar_rut(datos["rut_contacto"])
                datos["rut_contacto"] = normalizar_rut(datos["rut_contacto"])
            except Exception:  # noqa: BLE001 — el validador lanza el error de Django
                errores["rut_contacto"] = "El RUT no es válido."
        elif not con_cuenta:
            errores["rut_contacto"] = "Para comprar sin cuenta necesitamos tu RUT."

        if not con_cuenta and not datos.get("email_contacto"):
            errores["email_contacto"] = "Para comprar sin cuenta necesitamos tu correo."

        if errores:
            raise serializers.ValidationError(errores)
        return datos


class LineaPedidoDetalleSerializer(serializers.ModelSerializer):
    productoNombre = serializers.CharField(source="producto.nombre", read_only=True)
    productoCodigo = serializers.CharField(source="producto.codigo", read_only=True)
    precioUnitarioNeto = serializers.IntegerField(
        source="precio_unitario_neto", read_only=True
    )
    subtotalNeto = serializers.IntegerField(source="subtotal_neto", read_only=True)
    subtotalIva = serializers.IntegerField(source="subtotal_iva", read_only=True)
    subtotalTotal = serializers.IntegerField(source="subtotal_total", read_only=True)

    class Meta:
        model = LineaPedido
        fields = [
            "id",
            "productoNombre",
            "productoCodigo",
            "cantidad",
            "precioUnitarioNeto",
            "subtotalNeto",
            "subtotalIva",
            "subtotalTotal",
        ]


class PedidoDetalleSerializer(serializers.ModelSerializer):
    lineas = LineaPedidoDetalleSerializer(many=True, read_only=True)
    estadoVisible = serializers.CharField(source="get_estado_display", read_only=True)
    nombreContacto = serializers.CharField(source="nombre_contacto", read_only=True)
    telefonoContacto = serializers.CharField(source="telefono_contacto", read_only=True)
    emailContacto = serializers.CharField(source="email_contacto", read_only=True)
    direccionEntrega = serializers.CharField(source="direccion_entrega", read_only=True)
    totalNeto = serializers.IntegerField(source="total_neto", read_only=True)
    totalIva = serializers.IntegerField(source="total_iva", read_only=True)
    creadoEn = serializers.DateTimeField(source="fecha_creacion", read_only=True)

    class Meta:
        model = Pedido
        fields = [
            "id",
            "folio",
            "estado",
            "estadoVisible",
            "nombreContacto",
            "telefonoContacto",
            "emailContacto",
            "direccionEntrega",
            "notas",
            "totalNeto",
            "totalIva",
            "total",
            "creadoEn",
            "lineas",
        ]
