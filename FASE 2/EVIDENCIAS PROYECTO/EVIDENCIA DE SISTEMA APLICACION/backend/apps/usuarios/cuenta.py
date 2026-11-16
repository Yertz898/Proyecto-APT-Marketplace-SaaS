"""
La cuenta propia y el equipo de la tienda.

Dos cosas distintas en el mismo archivo porque comparten las reglas de la
contraseña. La cuenta propia la administra cualquiera que haya iniciado
sesión; el equipo, solo el dueño.
"""

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import generics, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView

from apps.auditoria.models import Accion
from apps.auditoria.registrar import registrar
from apps.core.permissions import EsDuenoDeTienda, PlanMinimo
from apps.usuarios.models import Rol, Usuario

# ── Cuenta propia ───────────────────────────────────────────────────────────


class CambiosDeCuentaSerializer(serializers.ModelSerializer):
    """Lo único que se edita de la propia cuenta es el nombre."""

    class Meta:
        model = Usuario
        fields = ["nombre"]


class CambioDeContrasenaSerializer(serializers.Serializer):
    actual = serializers.CharField(write_only=True)
    nueva = serializers.CharField(write_only=True)

    def validate_actual(self, valor):
        if not self.context["request"].user.check_password(valor):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return valor

    def validate(self, datos):
        validate_password(datos["nueva"], user=self.context["request"].user)
        if datos["nueva"] == datos["actual"]:
            raise serializers.ValidationError(
                {"nueva": "La contraseña nueva tiene que ser distinta de la actual."}
            )
        return datos


class CambiarContrasena(APIView):
    """
    POST /auth/contrasena: cambia la contraseña propia.

    Pide la actual aunque haya sesión: un navegador abierto y desatendido no
    tiene que bastar para quedarse con la cuenta. Lleva el mismo límite de
    frecuencia que el inicio de sesión, porque también sirve para probar
    contraseñas.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "autenticacion"

    def post(self, request):
        datos = CambioDeContrasenaSerializer(
            data=request.data, context={"request": request}
        )
        datos.is_valid(raise_exception=True)

        request.user.set_password(datos.validated_data["nueva"])
        request.user.save(update_fields=["password"])
        registrar(
            Accion.CUENTA,
            "contraseña",
            request.user.email,
            tienda=request.user.tienda,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Equipo de la tienda ─────────────────────────────────────────────────────


class MiembroSerializer(serializers.ModelSerializer):
    rolNombre = serializers.CharField(source="get_rol_display", read_only=True)
    activo = serializers.BooleanField(source="is_active", required=False)
    fechaRegistro = serializers.DateTimeField(source="fecha_registro", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "nombre",
            "email",
            "rol",
            "rolNombre",
            "activo",
            "fechaRegistro",
        ]
        read_only_fields = ["id", "email", "rol", "rolNombre", "fechaRegistro"]


class NuevoVendedorSerializer(serializers.ModelSerializer):
    """
    Alta de un vendedor por el dueño.

    El rol y la tienda no se reciben: el que se crea desde acá es siempre un
    vendedor de la tienda de quien lo crea.
    """

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Usuario.objects.all(),
                lookup="iexact",
                message="Ya hay una cuenta con este correo.",
            )
        ]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["nombre", "email", "password"]

    def validate_password(self, valor):
        validate_password(valor)
        return valor


class ContrasenaDeMiembroSerializer(serializers.Serializer):
    nueva = serializers.CharField(write_only=True)

    def validate_nueva(self, valor):
        validate_password(valor)
        return valor


PERMISOS_DE_EQUIPO = [EsDuenoDeTienda, PlanMinimo("premium")]


class EquipoDeLaTienda(generics.ListCreateAPIView):
    """
    GET y POST /panel/equipo: quién trabaja en la tienda, y alta de vendedores.

    La lista sale de la tienda del token. Una tienda no ve ni puede tocar a
    nadie de otra.
    """

    permission_classes = PERMISOS_DE_EQUIPO
    pagination_class = None

    def get_queryset(self):
        return Usuario.objects.filter(tienda_id=self.request.user.tienda_id).order_by(
            "rol", "nombre"
        )

    def get_serializer_class(self):
        return (
            NuevoVendedorSerializer
            if self.request.method == "POST"
            else MiembroSerializer
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        datos = NuevoVendedorSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        vendedor = Usuario.objects.create_user(
            email=datos.validated_data["email"],
            password=datos.validated_data["password"],
            nombre=datos.validated_data["nombre"],
            rol=Rol.VENDEDOR,
            tienda_id=request.user.tienda_id,
        )
        return Response(
            MiembroSerializer(vendedor).data, status=status.HTTP_201_CREATED
        )


class MiembroDelEquipo(generics.UpdateAPIView):
    """
    PATCH /panel/equipo/<id>: renombrar o desactivar a un vendedor.

    Desactivar y no borrar: sus pedidos y cargas siguen apuntando a él, y una
    cuenta desactivada no puede iniciar sesión. El dueño no se desactiva a sí
    mismo desde acá, porque dejaría la tienda sin nadie que la administre.
    """

    serializer_class = MiembroSerializer
    permission_classes = PERMISOS_DE_EQUIPO
    http_method_names = ["patch"]

    def get_object(self):
        miembro = Usuario.objects.filter(
            pk=self.kwargs["pk"], tienda_id=self.request.user.tienda_id
        ).first()
        if miembro is None:
            raise NotFound()
        return miembro

    def perform_update(self, serializer):
        miembro = serializer.instance
        if (
            miembro.rol == Rol.DUENO_TIENDA
            and serializer.validated_data.get("is_active") is False
        ):
            raise serializers.ValidationError(
                {"activo": "El dueño de la tienda no se puede desactivar."}
            )
        serializer.save()


class ContrasenaDelMiembro(APIView):
    """
    POST /panel/equipo/<id>/contrasena: el dueño le pone una contraseña nueva a
    un vendedor que olvidó la suya. La del propio dueño se cambia desde su
    cuenta, pidiendo la actual.
    """

    permission_classes = PERMISOS_DE_EQUIPO

    def post(self, request, pk):
        miembro = Usuario.objects.filter(
            pk=pk, tienda_id=request.user.tienda_id, rol=Rol.VENDEDOR
        ).first()
        if miembro is None:
            raise NotFound()

        datos = ContrasenaDeMiembroSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        miembro.set_password(datos.validated_data["nueva"])
        miembro.save(update_fields=["password"])
        registrar(
            Accion.CUENTA,
            "contraseña de un vendedor",
            miembro.email,
            tienda=request.user.tienda,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
