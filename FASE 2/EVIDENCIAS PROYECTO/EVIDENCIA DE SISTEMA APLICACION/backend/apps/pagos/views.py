"""
El retorno desde Webpay.

Transbank devuelve al navegador del cliente a esta dirección —por POST o por
GET, según el caso— con el resultado. Acá se confirma o anula, y se manda al
cliente a la página de su tienda que muestra cómo terminó.

No pide sesión ni token: quien llega es el navegador del cliente desde
Transbank. Lo que protege es que el token de Webpay solo lo conocen Transbank
y ese navegador, y que el resultado se le pregunta a Transbank, no se le cree
al navegador.
"""

from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.pagos import servicios
from apps.pagos.models import EstadoDelPago, Pago


def _ir_a_la_tienda(pago: Pago | None) -> HttpResponseRedirect:
    if pago is None:
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/")
    consulta = urlencode({"folio": pago.pedido.folio, "estado": pago.estado})
    return HttpResponseRedirect(
        f"{settings.FRONTEND_URL}/t/{pago.pedido.tienda.slug}/pago?{consulta}"
    )


class Retorno(APIView):
    """GET/POST /api/pagos/webpay/retorno."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return self._procesar(request.query_params)

    def post(self, request):
        # Transbank manda un formulario; se juntan los dos por si viene en ambos.
        datos = {**request.query_params.dict(), **request.data.dict()}
        return self._procesar(datos)

    def _procesar(self, datos):
        pagos = Pago.objects.select_related("pedido", "pedido__tienda")
        token = datos.get("token_ws")
        anulado = datos.get("TBK_TOKEN")
        orden = datos.get("TBK_ORDEN_COMPRA")

        # El cliente anuló en el formulario de Webpay (con o sin token_ws).
        if anulado:
            pago = pagos.filter(token=anulado).first()
            if pago:
                servicios.abortar(pago)
            return _ir_a_la_tienda(pago)

        if token:
            pago = pagos.filter(token=token).first()
            if pago:
                servicios.confirmar(pago)
            return _ir_a_la_tienda(pago)

        # Se le acabó el tiempo en Webpay: solo vuelve la orden de compra.
        if orden:
            pago = pagos.filter(
                orden_compra=orden, estado=EstadoDelPago.INICIADO
            ).first()
            if pago:
                servicios.abortar(pago, EstadoDelPago.VENCIDO)
            return _ir_a_la_tienda(pago)

        return _ir_a_la_tienda(None)
