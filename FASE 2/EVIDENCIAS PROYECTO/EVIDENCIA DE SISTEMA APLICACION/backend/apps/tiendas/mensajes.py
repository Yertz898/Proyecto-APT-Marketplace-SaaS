"""
Mensajes del dueño de una tienda cerrada a la administración.

Cuando la administración cierra una tienda, su dueño todavía puede iniciar
sesión, pero el panel se le reduce a una pantalla: la que le permite escribirle
a DealCommerce. El mensaje sale de su sesión. La tienda, el nombre y el correo
los pone el backend desde la cuenta, y la persona solo escribe qué necesita.
"""

from rest_framework import generics, serializers, status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import EsAdminPlataforma
from apps.tiendas.models import MensajeDeTienda
from apps.usuarios.models import Rol


class EsDuenoDeTiendaCerrada(BasePermission):
    """El dueño de una tienda que cerró la administración, y nadie más."""

    message = "Solo el dueño de una tienda cerrada puede escribir por acá."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.rol == Rol.DUENO_TIENDA
            and usuario.tienda_id
            and usuario.tienda.cerrada_por_la_plataforma
        )


class MensajeNuevoSerializer(serializers.Serializer):
    mensaje = serializers.CharField(max_length=2000)

    def validate_mensaje(self, valor):
        valor = valor.strip()
        if len(valor) < 5:
            raise serializers.ValidationError("Cuéntanos un poco más.")
        return valor


class EscribirALaPlataforma(APIView):
    """POST /panel/mensaje-a-la-plataforma: el dueño de una tienda cerrada escribe."""

    permission_classes = [EsDuenoDeTiendaCerrada]

    def post(self, request):
        datos = MensajeNuevoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)

        usuario = request.user
        MensajeDeTienda.objects.create(
            tienda=usuario.tienda,
            usuario=usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            mensaje=datos.validated_data["mensaje"],
        )
        return Response(
            {"mensaje": "Recibimos tu mensaje. Te vamos a escribir a tu correo."},
            status=status.HTTP_201_CREATED,
        )


class MensajeDePlataformaSerializer(serializers.ModelSerializer):
    tienda = serializers.CharField(source="tienda.nombre", read_only=True)
    tiendaSlug = serializers.CharField(source="tienda.slug", read_only=True)

    class Meta:
        model = MensajeDeTienda
        fields = [
            "id",
            "tienda",
            "tiendaSlug",
            "nombre",
            "email",
            "mensaje",
            "leido",
            "fecha",
        ]
        read_only_fields = [
            "id",
            "tienda",
            "tiendaSlug",
            "nombre",
            "email",
            "mensaje",
            "fecha",
        ]


class MensajesDePlataforma(generics.ListAPIView):
    """GET /plataforma/mensajes: lo que escribieron las tiendas cerradas."""

    permission_classes = [EsAdminPlataforma]
    serializer_class = MensajeDePlataformaSerializer
    pagination_class = None

    def get_queryset(self):
        return MensajeDeTienda.objects.select_related("tienda")


class MensajeDePlataforma(generics.UpdateAPIView):
    """PATCH /plataforma/mensajes/<id>: marcar como leído o no leído."""

    permission_classes = [EsAdminPlataforma]
    serializer_class = MensajeDePlataformaSerializer
    queryset = MensajeDeTienda.objects.select_related("tienda")
    http_method_names = ["patch"]
