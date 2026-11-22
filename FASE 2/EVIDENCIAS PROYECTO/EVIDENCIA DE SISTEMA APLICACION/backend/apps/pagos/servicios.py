"""
El pago de un pedido con Webpay, de punta a punta.

1. **Iniciar.** Al cerrar el pedido con `metodo: "webpay"`, el pedido se crea
   igual que siempre (pendiente y con el stock reservado) y se abre la
   transacción en Transbank. El navegador recibe la URL y el token para ir a
   pagar.
2. **Volver.** Transbank devuelve al cliente al retorno (`views.Retorno`):
   - con `token_ws`: se confirma la transacción. Autorizada, el pedido pasa a
     **confirmado**; rechazada, el pedido se **anula** y el stock vuelve.
   - con `TBK_TOKEN`: el cliente anuló el pago en Webpay. Se anula el pedido.
   - solo con `TBK_ORDEN_COMPRA`: se le acabó el tiempo en Webpay. Igual.
3. **Vencer.** Un pago iniciado que nunca volvió (el cliente cerró la
   pestaña) deja stock reservado. A los 15 minutos se anula: al iniciar un
   pago nuevo en la misma tienda, o con `manage.py anular_pagos_vencidos`.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.pagos import webpay
from apps.pagos.models import EstadoDelPago, Pago
from apps.pedidos.models import Pedido

#: Cuánto se espera a que vuelva un pago antes de soltar el stock.
VENCIMIENTO = timedelta(minutes=15)


def iniciar(pedido: Pedido, url_retorno: str) -> tuple[Pago, str]:
    """
    Abre la transacción en Transbank: el pago y la URL de Webpay.

    Lanza `webpay.ErrorDeWebpay` si Transbank no responde.
    """
    respuesta = webpay.crear(
        orden_compra=pedido.folio,
        sesion=f"{pedido.tienda.slug}-{pedido.pk}",
        monto=int(pedido.total),
        url_retorno=url_retorno,
    )
    return Pago.objects.create(
        tienda_id=pedido.tienda_id,
        pedido=pedido,
        token=respuesta["token"],
        orden_compra=pedido.folio,
        monto=int(pedido.total),
    ), respuesta["url"]


def confirmar(pago: Pago) -> Pago:
    """
    Confirma la transacción y deja el pedido según el resultado.

    Es idempotente: si el pago ya se procesó (el cliente recargó la página de
    retorno), no vuelve a llamar a Transbank.
    """
    if pago.estado != EstadoDelPago.INICIADO:
        return pago

    try:
        respuesta = webpay.confirmar(pago.token)
    except webpay.ErrorDeWebpay as error:
        respuesta = {"error": str(error)}

    autorizado = (
        respuesta.get("status") == "AUTHORIZED"
        and respuesta.get("response_code") == 0
        and int(respuesta.get("amount") or 0) == pago.monto
    )

    with transaction.atomic():
        pago.respuesta = respuesta
        if autorizado:
            pago.estado = EstadoDelPago.AUTORIZADO
            pago.codigo_autorizacion = str(respuesta.get("authorization_code") or "")
            numero = str((respuesta.get("card_detail") or {}).get("card_number") or "")
            pago.ultimos_digitos = numero[-4:]
            pedido = pago.pedido
            if pedido.estado == Pedido.Estado.PENDIENTE:
                pedido.estado = Pedido.Estado.CONFIRMADO
                pedido.save(update_fields=["estado", "fecha_edicion"])
        else:
            pago.estado = EstadoDelPago.RECHAZADO
            pago.pedido.anular()
        pago.save()
    return pago


def abortar(pago: Pago, estado: str = EstadoDelPago.ABORTADO) -> Pago:
    """El cliente no pagó (anuló o se le acabó el tiempo): se anula el pedido."""
    if pago.estado != EstadoDelPago.INICIADO:
        return pago
    with transaction.atomic():
        pago.estado = estado
        pago.save(update_fields=["estado", "fecha_edicion"])
        pago.pedido.anular()
    return pago


def anular_vencidos(tienda_id: int | None = None) -> int:
    """Anula los pagos iniciados hace más de 15 minutos. Devuelve cuántos."""
    limite = timezone.now() - VENCIMIENTO
    vencidos = Pago.objects.filter(
        estado=EstadoDelPago.INICIADO, fecha_creacion__lt=limite
    ).select_related("pedido")
    if tienda_id is not None:
        vencidos = vencidos.filter(tienda_id=tienda_id)
    cuantos = 0
    for pago in vencidos:
        abortar(pago, EstadoDelPago.VENCIDO)
        cuantos += 1
    return cuantos
