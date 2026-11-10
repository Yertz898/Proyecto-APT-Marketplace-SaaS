"""
El carrito y los pedidos.

**El carrito no calcula precios.** Se los pregunta a `precios.servicios`, que
es el mismo motor que usa la ficha del producto y el único lugar donde están
escritos los tramos. Tener la cuenta en dos partes no es duplicación
inofensiva: la ficha mostraba el precio por tramo y el carrito cobraba el
precio base, y el comprador veía los dos números en la misma visita.

El recorrido es cotizar y después confirmar. Cotizar no escribe nada y se
puede repetir; confirmar descuenta inventario con la fila bloqueada y deja el
pedido con una copia de los precios del momento, para que lo cobrado no cambie
aunque después cambie el catálogo.

El pago no se procesa acá. La tienda cierra sus ventas por WhatsApp, así que
lo que se devuelve es el folio y un mensaje listo para enviar.
"""

import urllib.parse
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.models import Producto
from apps.pedidos.models import LineaPedido, Pedido
from apps.pedidos.serializers import CheckoutSerializer, PedidoDetalleSerializer
from apps.precios.dinero import desglose
from apps.precios.servicios import cantidad_legible, cotizar
from apps.tiendas.models import Tienda


class LineaInvalida(Exception):
    """La línea no se puede cotizar. El mensaje se le muestra al comprador."""


def _revisar_carrito(tienda, lineas_pedidas) -> tuple[list, int, str | None]:
    """
    Cotiza cada línea del carrito. No escribe nada.

    Devuelve las líneas resueltas, el neto acumulado y el primer aviso de
    conveniencia que aparezca. Una línea rechazada no bota a las demás: se
    marca con su motivo y el comprador ve cuál corregir, que es lo mismo que
    hace la carga masiva con una planilla.
    """
    resueltas: list[dict] = []
    neto_total = 0
    aviso = None

    for item in lineas_pedidas:
        codigo = str(item.get("codigo") or "").strip()

        try:
            cantidad = Decimal(str(item.get("cantidad", 1)))
        except (InvalidOperation, TypeError):
            cantidad = None

        if cantidad is None or cantidad <= 0:
            resueltas.append(
                {
                    "codigo": codigo,
                    "nombre": codigo,
                    "detalle": "",
                    "neto": 0,
                    "rechazo": "La cantidad no es un número válido.",
                }
            )
            continue

        # `publicadas_de` y no `de_tienda`: lo desactivado o agotado no existe
        # para el comprador, y poder pedirlo por su código sería la puerta de
        # atrás de la vitrina.
        producto = Producto.objects.publicadas_de(tienda).filter(codigo=codigo).first()
        if producto is None:
            resueltas.append(
                {
                    "codigo": codigo,
                    "nombre": codigo,
                    "detalle": cantidad_entera_o_decimal(cantidad),
                    "neto": 0,
                    "rechazo": "Este producto ya no está disponible en la tienda.",
                }
            )
            continue

        cotizacion = cotizar(producto, cantidad)
        detalle = cantidad_legible(producto, cantidad)

        if not cotizacion.aceptada:
            resueltas.append(
                {
                    "codigo": codigo,
                    "producto": producto,
                    "nombre": producto.nombre,
                    "detalle": detalle,
                    "neto": 0,
                    "rechazo": cotizacion.rechazo,
                }
            )
            continue

        neto_total += cotizacion.neto
        aviso = aviso or cotizacion.aviso
        resueltas.append(
            {
                "codigo": codigo,
                "producto": producto,
                "nombre": producto.nombre,
                "detalle": detalle,
                "neto": cotizacion.neto,
                "rechazo": None,
                "cantidad": cantidad,
                "precio_unitario": cotizacion.precio_unitario,
                "iva": cotizacion.iva,
                "total": cotizacion.total,
            }
        )

    return resueltas, neto_total, aviso


def cantidad_entera_o_decimal(cantidad: Decimal) -> str:
    """La cantidad sola, para cuando no hay producto del cual sacar la unidad."""
    if cantidad == cantidad.to_integral_value():
        return str(int(cantidad))
    return str(cantidad.normalize()).replace(".", ",")


class CotizarCarritoView(APIView):
    """
    POST /api/t/<slug>/carrito/cotizar

    Qué cuesta el carrito completo, con los tramos aplicados. No escribe nada,
    así que el carrito puede preguntarlo en cada cambio de cantidad.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, slug):
        tienda = get_object_or_404(Tienda, slug=slug)
        lineas, neto_total, aviso = _revisar_carrito(
            tienda, request.data.get("lineas", [])
        )

        hay_rechazo = any(linea["rechazo"] for linea in lineas)
        cifras = desglose(neto_total)

        return Response(
            {
                "neto": cifras["neto"],
                "iva": cifras["iva"],
                "total": cifras["total"],
                "avisoTramo": aviso,
                "rechazo": (
                    "Corrige los productos marcados para continuar."
                    if hay_rechazo
                    else None
                ),
                "lineas": [
                    {
                        "nombre": linea["nombre"],
                        "detalle": linea["detalle"],
                        "neto": linea["neto"],
                        "rechazo": linea["rechazo"],
                    }
                    for linea in lineas
                ],
            }
        )


class ConfirmarPedidoView(APIView):
    """
    POST /api/t/<slug>/pedidos

    Cierra el pedido: descuenta inventario, guarda los precios del momento y
    devuelve el folio con el mensaje de WhatsApp.

    Se vuelve a cotizar acá en vez de confiar en lo que mandó el navegador.
    Entre cotizar y confirmar pasa tiempo, y en ese rato el precio pudo
    cambiar o el último lote pudo venderse.
    """

    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, slug):
        tienda = get_object_or_404(Tienda, slug=slug)

        datos = CheckoutSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        contacto = datos.validated_data

        lineas, neto_total, _ = _revisar_carrito(tienda, contacto["lineas"])

        rechazadas = [linea for linea in lineas if linea["rechazo"]]
        if rechazadas:
            raise ValidationError(
                {
                    "error": "Hay productos que ya no se pueden pedir.",
                    "lineas": [
                        {"codigo": linea["codigo"], "motivo": linea["rechazo"]}
                        for linea in rechazadas
                    ],
                }
            )

        cifras = desglose(neto_total)
        pedido = Pedido.objects.create(
            tienda=tienda,
            comprador=request.user if request.user.is_authenticated else None,
            nombre_contacto=contacto["nombre_contacto"],
            telefono_contacto=contacto["telefono_contacto"],
            email_contacto=contacto["email_contacto"],
            direccion_entrega=contacto["direccion_entrega"],
            notas=contacto["notas"],
            total_neto=cifras["neto"],
            total_iva=cifras["iva"],
            total=cifras["total"],
            estado=Pedido.Estado.PENDIENTE,
        )

        for linea in lineas:
            self._descontar(linea)
            LineaPedido.objects.create(
                pedido=pedido,
                producto=linea["producto"],
                cantidad=linea["cantidad"],
                precio_unitario_neto=linea["precio_unitario"],
                subtotal_neto=linea["neto"],
                subtotal_iva=linea["iva"],
                subtotal_total=linea["total"],
            )

        return Response(
            {
                "numero": pedido.folio,
                "mensaje": (
                    "Tu pedido quedó registrado con el folio "
                    f"{pedido.folio}. Escríbele a la tienda para coordinar el "
                    "pago y la entrega."
                ),
                "enlaceWhatsapp": _enlace_de_whatsapp(tienda, pedido, lineas),
            },
            status=status.HTTP_201_CREATED,
        )

    def _descontar(self, linea) -> None:
        """
        Baja el inventario con la fila bloqueada.

        El bloqueo es lo que impide que dos compradores simultáneos se lleven
        el mismo último lote: el segundo espera a que el primero termine y
        entonces ve el stock ya descontado. Quien no lleva inventario no
        descuenta nada, porque la tienda no sabe cuánto le queda.
        """
        producto = linea["producto"]
        if not producto.controla_stock:
            return

        bloqueado = Producto.objects.select_for_update().get(pk=producto.pk)
        if bloqueado.stock < linea["cantidad"]:
            raise ValidationError(
                {
                    "error": (
                        f"Alguien se adelantó: quedan "
                        f"{cantidad_legible(bloqueado, bloqueado.stock)} de "
                        f"{bloqueado.nombre}."
                    )
                }
            )

        bloqueado.stock -= linea["cantidad"]
        bloqueado.save(update_fields=["stock"])


def _pesos(monto) -> str:
    """En pesos chilenos: punto de miles y sin decimales."""
    return f"${int(monto):,}".replace(",", ".")


def _enlace_de_whatsapp(tienda, pedido, lineas) -> str | None:
    """
    El mensaje listo para enviarle a la tienda, o None si no tiene WhatsApp.

    Antes, una tienda sin WhatsApp recibía un enlace a un número inventado. Es
    peor que no tener enlace: el comprador cree que avisó y nadie leyó nada.
    """
    if not tienda.whatsapp:
        return None

    detalle = "\n".join(
        f"• {linea['detalle']} de {linea['nombre']}" for linea in lineas
    )
    mensaje = (
        f"¡Hola {tienda.nombre}! Acabo de confirmar mi pedido:\n\n"
        f"Folio: {pedido.folio}\n"
        f"Detalle:\n{detalle}\n\n"
        f"Total: {_pesos(pedido.total)} con IVA\n\n"
        "Quedo atento para coordinar el pago."
    )

    partes = urllib.parse.urlsplit(tienda.whatsapp)
    consulta = urllib.parse.parse_qsl(partes.query)
    consulta.append(("text", mensaje))
    return urllib.parse.urlunsplit(
        partes._replace(query=urllib.parse.urlencode(consulta))
    )


class PedidoPanelListView(APIView):
    """
    GET /api/panel/pedidos/

    La bandeja del dueño. Sale de la tienda del token y no de la URL: un
    identificador en la ruta es algo que se puede cambiar a mano.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tienda = getattr(request.user, "tienda", None)
        if not tienda:
            raise NotFound(detail="No tienes una tienda asociada.")

        pedidos = (
            Pedido.objects.filter(tienda=tienda)
            .prefetch_related("lineas__producto")
            .order_by("-creado_en")
        )
        return Response(PedidoDetalleSerializer(pedidos, many=True).data)


class PedidoPanelEstadoView(APIView):
    """
    PATCH /api/panel/pedidos/<pk>/estado/

    Cambia el estado de un pedido. Anularlo devuelve el inventario.

    Un pedido de otra tienda responde 404 y no 403: que exista ya es
    información que no le corresponde a quien pregunta.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        tienda = getattr(request.user, "tienda", None)
        if not tienda:
            raise NotFound(detail="No tienes una tienda asociada.")

        pedido = get_object_or_404(Pedido, pk=pk, tienda=tienda)

        nuevo_estado = request.data.get("estado")
        if nuevo_estado not in Pedido.Estado.values:
            raise ValidationError({"estado": "Ese estado no existe."})

        if nuevo_estado == Pedido.Estado.CANCELADO:
            pedido.anular()
        else:
            pedido.estado = nuevo_estado
            pedido.save(update_fields=["estado", "actualizado_en"])

        return Response(PedidoDetalleSerializer(pedido).data)
