"""
El plan de la tienda, visto y cambiado por su dueño.

No hay cobro en línea: el cambio es inmediato y la facturación se coordina
fuera de la plataforma, igual que el pago de los pedidos. Cada cambio queda en
el registro de actividad, que es lo que la administración revisa para cobrar.
"""

from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import Accion
from apps.auditoria.registrar import registrar
from apps.core.permissions import EsDuenoDeTienda
from apps.tiendas.models import Plan

PRECIOS = {
    Plan.BASICO: 10990,
    Plan.PREMIUM: 20990,
    Plan.ULTIMATE: 35990,
}

INCLUYE = {
    Plan.BASICO: "Catálogo, inventario, precios por volumen, carga masiva y pedidos.",
    Plan.PREMIUM: "Suma tu marca, el panel de ventas, el equipo y la agenda.",
    Plan.ULTIMATE: "Suma pronóstico de demanda, segmentos de clientes y asistente.",
}


def estado_del_plan(tienda) -> dict:
    return {
        "plan": tienda.plan,
        "canceladaEn": tienda.cancelada_en,
        "planes": [
            {
                "plan": valor,
                "nombre": nombre,
                "precioNeto": PRECIOS[valor],
                "incluye": INCLUYE[valor],
            }
            for valor, nombre in Plan.choices
        ],
    }


class CambioDePlanSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=Plan.choices)


class PlanDeLaTienda(APIView):
    """
    GET /panel/plan: el plan actual y los disponibles.
    PATCH /panel/plan: cambia de plan.

    Solo el dueño: el plan es facturación, y el vendedor no factura.
    """

    permission_classes = [EsDuenoDeTienda]

    def get(self, request):
        return Response(estado_del_plan(request.user.tienda))

    def patch(self, request):
        datos = CambioDePlanSerializer(data=request.data)
        datos.is_valid(raise_exception=True)

        tienda = request.user.tienda
        if tienda.cancelada_en:
            raise serializers.ValidationError(
                {
                    "plan": "La suscripción está cancelada. Reanúdala antes de "
                    "cambiar de plan."
                }
            )

        anterior = tienda.plan
        tienda.plan = datos.validated_data["plan"]
        tienda.save(update_fields=["plan"])
        registrar(
            Accion.PLAN,
            "plan",
            f"{anterior} → {tienda.plan}",
            tienda=tienda,
            detalle={"plan": {"antes": anterior, "despues": tienda.plan}},
        )
        return Response(estado_del_plan(tienda))


class CancelarPlan(APIView):
    """
    POST /panel/plan/cancelar: cancela la suscripción.

    La vitrina se cierra al público en el acto, pero no se borra nada: el
    catálogo, los pedidos y las cuentas siguen ahí si la tienda vuelve.
    """

    permission_classes = [EsDuenoDeTienda]

    def post(self, request):
        tienda = request.user.tienda
        if not tienda.cancelada_en:
            tienda.cancelada_en = timezone.now()
            tienda.activa = False
            tienda.save(update_fields=["cancelada_en", "activa"])
        return Response(estado_del_plan(tienda))


class ReanudarPlan(APIView):
    """POST /panel/plan/reanudar: vuelve a abrir una suscripción cancelada."""

    permission_classes = [EsDuenoDeTienda]

    def post(self, request):
        tienda = request.user.tienda
        if tienda.cancelada_en:
            tienda.cancelada_en = None
            tienda.activa = True
            tienda.save(update_fields=["cancelada_en", "activa"])
        return Response(estado_del_plan(tienda))
