"""
Mensajes del equipo de una tienda cerrada a la administración.

Quien escribe no tiene sesión: su tienda está cerrada y el inicio de sesión lo
rechaza. Por eso el mensaje se manda con el correo y la contraseña, que se
vuelven a verificar acá. Sin eso, cualquiera podría escribir a nombre de
cualquier tienda. Lleva el mismo límite de frecuencia que el inicio de sesión.
"""

from django.contrib.auth import authenticate
from rest_framework import generics, serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.permissions import EsAdminPlataforma
from apps.tiendas.models import MensajeDeTienda


class MensajeNuevoSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mensaje = serializers.CharField(max_length=2000)


class EscribirALaPlataforma(APIView):
    """POST /auth/mensaje-a-la-plataforma: solo para el equipo de una tienda cerrada."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "autenticacion"

    def post(self, request):
        datos = MensajeNuevoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        v = datos.validated_data

        usuario = authenticate(
            request, email=v["email"].lower(), password=v["password"]
        )
        if usuario is None:
            raise AuthenticationFailed()

        tienda = usuario.tienda if usuario.tienda_id else None
        if tienda is None or not tienda.cerrada_por_la_plataforma:
            # Una tienda abierta escribe desde su panel, no desde acá.
            raise serializers.ValidationError(
                {"general": "Tu tienda no está cerrada: entra al panel normalmente."}
            )

        MensajeDeTienda.objects.create(
            tienda=tienda,
            usuario=usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            mensaje=v["mensaje"].strip(),
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
