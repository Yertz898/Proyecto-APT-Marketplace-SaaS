import urllib.parse
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError, NotFound

from apps.tiendas.models import Tienda
from apps.catalogo.models import Producto
from apps.pedidos.models import Pedido, LineaPedido
from apps.pedidos.serializers import PedidoDetalleSerializer


class CotizarCarritoView(APIView):
    """
    POST /api/t/<slug>/carrito/cotizar/
    Calcula el neto, IVA, totales y valida stock/cupos en tiempo real para vista-carrito.tsx.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, slug):
        tienda = get_object_or_404(Tienda, slug=slug)
        lineas_input = request.data.get('lineas', [])

        total_neto = Decimal('0.00')
        lineas_cotizadas = []
        aviso_tramo_global = None
        hay_rechazo_global = False

        for item in lineas_input:
            codigo = item.get('codigo')
            cantidad = Decimal(str(item.get('cantidad', 1)))

            producto = Producto.objects.filter(tienda=tienda, codigo=codigo).first()
            if not producto:
                lineas_cotizadas.append({
                    'nombre': codigo,
                    'detalle': f"{cantidad}",
                    'neto': 0,
                    'rechazo': 'Producto no disponible en esta tienda.'
                })
                hay_rechazo_global = True
                continue

            # Validación preventiva de inventario
            rechazo_linea = None
            if hasattr(producto, 'stock') and producto.stock is not None:
                if producto.stock < cantidad:
                    rechazo_linea = f"Solo quedan {producto.stock} unidades disponibles."
                    hay_rechazo_global = True
            elif hasattr(producto, 'cupos_disponibles') and producto.cupos_disponibles is not None:
                if producto.cupos_disponibles < int(cantidad):
                    rechazo_linea = f"Solo quedan {producto.cupos_disponibles} cupos disponibles."
                    hay_rechazo_global = True

            # Redacción del detalle según la forma de venta (unidad, lote o peso)
            forma = getattr(producto, 'forma_venta', 'unidad')
            if forma == 'lote':
                detalle_texto = f"{int(cantidad)} lote{'s' if cantidad > 1 else ''}"
            elif forma == 'peso':
                detalle_texto = f"{cantidad} g"
            else:
                detalle_texto = f"{int(cantidad)} un."

            # Resolución de precio neto base o por tramos
            precio_unitario = getattr(producto, 'precio_neto', Decimal('1000.00'))
            if hasattr(producto, 'calcular_precio_tramo'):
                precio_unitario = producto.calcular_precio_tramo(cantidad)

            if hasattr(producto, 'obtener_aviso_conveniencia'):
                aviso = producto.obtener_aviso_conveniencia(cantidad)
                if aviso and not aviso_tramo_global:
                    aviso_tramo_global = aviso

            subtotal_linea = (precio_unitario * cantidad).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            total_neto += subtotal_linea

            lineas_cotizadas.append({
                'nombre': producto.nombre,
                'detalle': detalle_texto,
                'neto': int(subtotal_linea),
                'rechazo': rechazo_linea
            })

        total_iva = (total_neto * Decimal('0.19')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        total_final = total_neto + total_iva

        return Response({
            'neto': int(total_neto),
            'iva': int(total_iva),
            'total': int(total_final),
            'avisoTramo': aviso_tramo_global,
            'rechazo': 'Corrige los productos marcados para continuar.' if hay_rechazo_global else None,
            'lineas': lineas_cotizadas
        })


class ConfirmarPedidoView(APIView):
    """
    POST /api/t/<slug>/pedidos/
    Reserva de inventario con select_for_update(), cálculo de totales y enlace de WhatsApp.
    """
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, slug):
        tienda = get_object_or_404(Tienda, slug=slug)
        lineas_input = request.data.get('lineas', [])

        if not lineas_input:
            return Response({'error': 'El carrito no tiene productos.'}, status=status.HTTP_400_BAD_REQUEST)

        total_neto_acumulado = Decimal('0.00')
        lineas_a_guardar = []

        # Bloqueo atómico con select_for_update() para evitar condiciones de carrera
        for item in lineas_input:
            codigo = item.get('codigo')
            cantidad = Decimal(str(item.get('cantidad', 1)))

            try:
                producto = (
                    Producto.objects.select_for_update()
                    .get(tienda=tienda, codigo=codigo)
                )
            except Producto.DoesNotExist:
                return Response(
                    {'error': f"El producto {codigo} no existe en esta tienda."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Descuento de stock o cupos
            if hasattr(producto, 'stock') and producto.stock is not None:
                if producto.stock < cantidad:
                    return Response(
                        {'error': f"Stock insuficiente para {producto.nombre}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                producto.stock -= cantidad
                producto.save(update_fields=['stock'])
            elif hasattr(producto, 'cupos_disponibles') and producto.cupos_disponibles is not None:
                if producto.cupos_disponibles < int(cantidad):
                    return Response(
                        {'error': f"Cupos agotados para {producto.nombre}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                producto.cupos_disponibles -= int(cantidad)
                producto.save(update_fields=['cupos_disponibles'])

            precio_unitario = getattr(producto, 'precio_neto', Decimal('1000.00'))
            if hasattr(producto, 'calcular_precio_tramo'):
                precio_unitario = producto.calcular_precio_tramo(cantidad)

            sub_neto = (precio_unitario * cantidad).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            sub_iva = (sub_neto * Decimal('0.19')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            sub_total = sub_neto + sub_iva

            total_neto_acumulado += sub_neto
            lineas_a_guardar.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario_neto': precio_unitario,
                'subtotal_neto': sub_neto,
                'subtotal_iva': sub_iva,
                'subtotal_total': sub_total,
            })

        total_iva = (total_neto_acumulado * Decimal('0.19')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        total_general = total_neto_acumulado + total_iva

        nombre_cliente = "Cliente Vitrina"
        if request.user.is_authenticated:
            nombre_cliente = request.user.get_full_name() or request.user.username

        pedido = Pedido.objects.create(
            tienda=tienda,
            comprador=request.user if request.user.is_authenticated else None,
            nombre_contacto=nombre_cliente,
            telefono_contacto=getattr(request.user, 'telefono', '') or 'Por coordinar',
            total_neto=total_neto_acumulado,
            total_iva=total_iva,
            total=total_general,
            estado=Pedido.Estado.PENDIENTE
        )

        for l in lineas_a_guardar:
            LineaPedido.objects.create(pedido=pedido, **l)

        # Enlace preformateado de WhatsApp
        telefono_tienda = getattr(tienda, 'telefono_contacto', '') or '56900000000'
        detalle_msg = "\n".join([f"• {l['cantidad']}x {l['producto'].nombre}" for l in lineas_a_guardar])
        mensaje = (
            f"¡Hola {tienda.nombre}! Acabo de confirmar mi pedido:\n\n"
            f"📦 *Folio:* {pedido.folio}\n"
            f"📋 *Detalle:*\n{detalle_msg}\n\n"
            f"💰 *Total estimado:* ${pedido.total:,} (IVA incl.)\n\n"
            f"Quedo a la espera de sus datos para transferir."
        )
        url_ws = f"https://wa.me/{telefono_tienda}?text={urllib.parse.quote(mensaje)}"

        return Response({
            'numero': pedido.folio,
            'mensaje': f"Tu pedido ha sido registrado con éxito bajo el folio {pedido.folio}.",
            'enlaceWhatsapp': url_ws
        }, status=status.HTTP_201_CREATED)


class PedidoPanelListView(APIView):
    """
    GET /api/panel/pedidos/
    Bandeja de pedidos del vendedor/dueño autenticado (aislado estrictamente por tenant).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tienda_usuario = getattr(request.user, 'tienda', None)
        if not tienda_usuario:
            raise NotFound(detail="No tienes una tienda asociada.")

        pedidos = Pedido.objects.filter(tienda=tienda_usuario).order_by('-creado_en')
        return Response(PedidoDetalleSerializer(pedidos, many=True).data)


class PedidoPanelEstadoView(APIView):
    """
    PATCH /api/panel/pedidos/<int:pk>/estado/
    Actualiza el estado de la orden. Si se anula (CANCELADO), restituye el inventario.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        tienda_usuario = getattr(request.user, 'tienda', None)
        if not tienda_usuario:
            raise NotFound(detail="Tienda no encontrada.")

        # Regla multi-tenant: 404 si el pedido pertenece a otra tienda
        pedido = get_object_or_404(Pedido, pk=pk, tienda=tienda_usuario)

        nuevo_estado = request.data.get('estado')
        if nuevo_estado not in Pedido.Estado.values:
            raise ValidationError({'estado': 'Estado no válido.'})

        if nuevo_estado == Pedido.Estado.CANCELADO:
            pedido.anular()
        else:
            pedido.estado = nuevo_estado
            pedido.save(update_fields=['estado', 'actualizado_en'])

        return Response(PedidoDetalleSerializer(pedido).data)