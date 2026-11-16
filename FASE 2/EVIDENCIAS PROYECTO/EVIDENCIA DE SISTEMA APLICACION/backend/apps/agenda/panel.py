"""
La agenda vista desde el panel: horarios, días cerrados y visitas.

La vitrina ya ofrecía horas y recibía solicitudes; acá el dueño o un vendedor
define cuándo atiende y responde cada solicitud. Todo se acota a la tienda del
token, y la sección pide el plan Premium.
"""

from django.core.exceptions import ValidationError as ErrorDeDjango
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import generics, serializers
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agenda.disponibilidad import asiento_libre, capacidad_de_la_hora
from apps.agenda.models import (
    ESTADOS_QUE_OCUPAN,
    BloqueHorario,
    ConfiguracionAgenda,
    DiaBloqueado,
    EstadoVisita,
    Visita,
)
from apps.core.mixins import MixinTiendaDelUsuario
from apps.core.permissions import PlanMinimo, TrabajaEnLaTienda

PERMISOS = [TrabajaEnLaTienda, PlanMinimo("premium")]


def _como_error_de_api(error: ErrorDeDjango):
    detalle = (
        error.message_dict
        if hasattr(error, "error_dict")
        else {"detalle": error.messages}
    )
    return serializers.ValidationError(detalle)


# ── Configuración ───────────────────────────────────────────────────────────


class ConfiguracionSerializer(serializers.ModelSerializer):
    duracionMinutos = serializers.IntegerField(
        source="duracion_minutos", min_value=5, max_value=480
    )
    visitasPorBloque = serializers.IntegerField(
        source="visitas_por_bloque", min_value=1, max_value=50
    )
    anticipacionMinimaHoras = serializers.IntegerField(
        source="anticipacion_minima_horas", min_value=0, max_value=720
    )
    ventanaMaximaDias = serializers.IntegerField(
        source="ventana_maxima_dias", min_value=1, max_value=180
    )
    confirmacionAutomatica = serializers.BooleanField(source="confirmacion_automatica")
    correoNotificaciones = serializers.EmailField(
        source="correo_notificaciones", required=False, allow_blank=True
    )

    class Meta:
        model = ConfiguracionAgenda
        fields = [
            "duracionMinutos",
            "visitasPorBloque",
            "anticipacionMinimaHoras",
            "ventanaMaximaDias",
            "confirmacionAutomatica",
            "direccion",
            "indicaciones",
            "correoNotificaciones",
        ]


class ConfiguracionDeAgenda(generics.RetrieveUpdateAPIView):
    """GET y PATCH /panel/agenda/configuracion. Se crea la primera vez que se pide."""

    serializer_class = ConfiguracionSerializer
    permission_classes = PERMISOS
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        configuracion, _ = ConfiguracionAgenda.objects.get_or_create(
            tienda_id=self.request.user.tienda_id
        )
        return configuracion


# ── Bloques de atención ─────────────────────────────────────────────────────


class BloqueSerializer(serializers.ModelSerializer):
    diaSemana = serializers.IntegerField(
        source="dia_semana", required=False, allow_null=True, min_value=0, max_value=6
    )
    horaInicio = serializers.TimeField(source="hora_inicio", format="%H:%M")
    horaFin = serializers.TimeField(source="hora_fin", format="%H:%M")
    duracionMinutos = serializers.IntegerField(
        source="duracion_minutos", required=False, allow_null=True, min_value=5
    )
    visitasSimultaneas = serializers.IntegerField(
        source="visitas_simultaneas", required=False, allow_null=True, min_value=1
    )

    class Meta:
        model = BloqueHorario
        fields = [
            "id",
            "nombre",
            "diaSemana",
            "fecha",
            "horaInicio",
            "horaFin",
            "duracionMinutos",
            "visitasSimultaneas",
        ]

    def validate(self, datos):
        # El modelo valida lo suyo (que no se crucen, que sea semanal o puntual),
        # así que se arma la instancia y se le pregunta antes de guardar.
        instancia = self.instance or BloqueHorario()
        for campo, valor in datos.items():
            setattr(instancia, campo, valor)
        instancia.tienda_id = self.context["request"].user.tienda_id
        if (
            instancia.hora_inicio
            and instancia.hora_fin
            and instancia.hora_fin <= instancia.hora_inicio
        ):
            raise serializers.ValidationError(
                {"horaFin": "Tiene que terminar después de empezar."}
            )
        if (instancia.dia_semana is None) == (instancia.fecha is None):
            raise serializers.ValidationError(
                {"diaSemana": "Elige un día de la semana o una fecha, no las dos."}
            )
        try:
            instancia.validar_sin_solapes()
        except ErrorDeDjango as error:
            raise _como_error_de_api(error) from None
        return datos


class BloquesDeAgenda(MixinTiendaDelUsuario, generics.ListCreateAPIView):
    serializer_class = BloqueSerializer
    permission_classes = PERMISOS
    queryset = BloqueHorario.objects.all()
    pagination_class = None


class BloqueDeAgenda(MixinTiendaDelUsuario, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BloqueSerializer
    permission_classes = PERMISOS
    queryset = BloqueHorario.objects.all()
    http_method_names = ["get", "patch", "delete", "head", "options"]


# ── Días cerrados ───────────────────────────────────────────────────────────


class DiaBloqueadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaBloqueado
        fields = ["id", "fecha", "motivo"]


class DiasBloqueados(MixinTiendaDelUsuario, generics.ListCreateAPIView):
    serializer_class = DiaBloqueadoSerializer
    permission_classes = PERMISOS
    queryset = DiaBloqueado.objects.all()
    pagination_class = None

    def get_queryset(self):
        # Los días que ya pasaron no le sirven a nadie en la pantalla.
        return (
            super()
            .get_queryset()
            .filter(fecha__gte=timezone.localdate())
            .order_by("fecha")
        )

    def perform_create(self, serializer):
        tienda_id = self.request.user.tienda_id
        if DiaBloqueado.objects.filter(
            tienda_id=tienda_id, fecha=serializer.validated_data["fecha"]
        ).exists():
            raise serializers.ValidationError({"fecha": "Ese día ya está cerrado."})
        super().perform_create(serializer)


class DiaBloqueadoDetalle(MixinTiendaDelUsuario, generics.DestroyAPIView):
    serializer_class = DiaBloqueadoSerializer
    permission_classes = PERMISOS
    queryset = DiaBloqueado.objects.all()


# ── Visitas ─────────────────────────────────────────────────────────────────


class VisitaDelPanelSerializer(serializers.ModelSerializer):
    estadoNombre = serializers.CharField(source="get_estado_display", read_only=True)
    nombreContacto = serializers.CharField(source="nombre_contacto")
    correoContacto = serializers.CharField(source="correo_contacto")
    telefonoContacto = serializers.CharField(source="telefono_contacto")
    motivoRechazo = serializers.CharField(source="motivo_rechazo")
    siguientes = serializers.SerializerMethodField()
    horaTomada = serializers.SerializerMethodField()

    class Meta:
        model = Visita
        fields = [
            "id",
            "inicio",
            "fin",
            "estado",
            "estadoNombre",
            "nombreContacto",
            "correoContacto",
            "telefonoContacto",
            "motivo",
            "motivoRechazo",
            "siguientes",
            "horaTomada",
        ]

    def get_siguientes(self, visita):
        from apps.agenda.models import TRANSICIONES

        return sorted(TRANSICIONES[visita.estado])

    def get_horaTomada(self, visita):  # noqa: N802 — nombre del campo
        """
        Una solicitud cuya hora ya llenó otra visita confirmada.

        El panel la marca para que el vendedor sepa que no puede confirmarla y
        le toca rechazarla o proponerle otra hora.
        """
        if visita.estado != EstadoVisita.SOLICITADA:
            return False
        configuracion = ConfiguracionAgenda.objects.filter(
            tienda_id=visita.tienda_id
        ).first()
        if configuracion is None:
            return False
        confirmadas = Visita.objects.filter(
            tienda_id=visita.tienda_id,
            inicio=visita.inicio,
            estado__in=ESTADOS_QUE_OCUPAN,
        ).count()
        return confirmadas >= capacidad_de_la_hora(configuracion, visita.inicio)


class VisitasDeLaTienda(MixinTiendaDelUsuario, generics.ListAPIView):
    """
    GET /panel/agenda/visitas: las visitas desde hoy, o todas con ?todas=1.

    Se puede filtrar por estado.
    """

    serializer_class = VisitaDelPanelSerializer
    permission_classes = PERMISOS
    queryset = Visita.objects.all()
    pagination_class = None

    def get_queryset(self):
        visitas = super().get_queryset().order_by("inicio")
        if self.request.query_params.get("todas") != "1":
            visitas = visitas.filter(inicio__date__gte=timezone.localdate())
        estado = self.request.query_params.get("estado")
        if estado in EstadoVisita.values:
            visitas = visitas.filter(estado=estado)
        return visitas


class CambioDeEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=EstadoVisita.choices)
    motivoRechazo = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )


class EstadoDeVisita(APIView):
    """POST /panel/agenda/visitas/<id>/estado: confirmar, rechazar o marcar."""

    permission_classes = PERMISOS

    def post(self, request, pk):
        visita = Visita.objects.de_usuario(request.user).filter(pk=pk).first()
        if visita is None:
            raise NotFound()

        datos = CambioDeEstadoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        nuevo = datos.validated_data["estado"]

        try:
            with transaction.atomic():
                visita.cambiar_estado(
                    nuevo, motivo_rechazo=datos.validated_data.get("motivoRechazo", "")
                )
                if nuevo == EstadoVisita.CONFIRMADA:
                    visita.posicion = self._asiento(visita)
                visita.save()
        except ErrorDeDjango as error:
            raise _como_error_de_api(error) from None
        except IntegrityError:
            # Dos confirmaciones al mismo tiempo por el último cupo: el índice
            # único del asiento deja pasar a una sola.
            raise serializers.ValidationError(
                {"estado": "Esa hora se acaba de tomar. Rechaza esta o propón otra."}
            ) from None
        return Response(VisitaDelPanelSerializer(visita).data)

    def _asiento(self, visita) -> int:
        """
        El cupo que toma la visita al confirmarse, o un error si ya no queda.

        Es acá, y no al pedirla, donde la hora pasa a estar tomada.
        """
        configuracion, _ = ConfiguracionAgenda.objects.get_or_create(
            tienda_id=visita.tienda_id
        )
        # Bloquear las visitas de esa hora serializa a dos vendedores que
        # confirman a la vez.
        list(
            Visita.objects.select_for_update()
            .filter(tienda_id=visita.tienda_id, inicio=visita.inicio)
            .values_list("pk", flat=True)
        )
        capacidad = capacidad_de_la_hora(configuracion, visita.inicio)
        asiento = asiento_libre(visita.tienda_id, visita.inicio, capacidad)
        if asiento is None:
            raise serializers.ValidationError(
                {
                    "estado": "Esa hora ya está tomada por otra visita confirmada. "
                    "Rechaza esta o propón otra hora."
                }
            )
        return asiento
