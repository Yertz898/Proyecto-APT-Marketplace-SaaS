"""
La administración de DealCommerce: las tiendas, las solicitudes y el registro.

Todo lo de acá es solo para el administrador de la plataforma. Es el único
lugar del sistema que ve más de una tienda a la vez, así que cada vista exige
el permiso explícitamente y no hereda el filtro por tienda.
"""

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import generics, serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from apps.auditoria.models import Registro
from apps.core.permissions import EsAdminPlataforma
from apps.tiendas.models import (
    EstadoSolicitud,
    Plan,
    Plantilla,
    SolicitudDeAcceso,
    Tienda,
)
from apps.usuarios.models import Rol, Usuario

# ── Tiendas ─────────────────────────────────────────────────────────────────


class TiendaDePlataformaSerializer(serializers.ModelSerializer):
    canceladaEn = serializers.DateTimeField(source="cancelada_en", read_only=True)
    fechaCreacion = serializers.DateTimeField(source="fecha_creacion", read_only=True)
    dueno = serializers.SerializerMethodField()
    productos = serializers.IntegerField(source="n_productos", read_only=True)
    pedidos = serializers.IntegerField(source="n_pedidos", read_only=True)
    usuarios = serializers.IntegerField(source="n_usuarios", read_only=True)

    class Meta:
        model = Tienda
        fields = [
            "id",
            "slug",
            "nombre",
            "plan",
            "plantilla",
            "activa",
            "canceladaEn",
            "fechaCreacion",
            "dueno",
            "productos",
            "pedidos",
            "usuarios",
        ]
        read_only_fields = ["id", "slug"]

    def get_dueno(self, tienda):
        dueno = tienda.usuarios.filter(rol=Rol.DUENO_TIENDA).order_by("id").first()
        return {"nombre": dueno.nombre, "email": dueno.email} if dueno else None


class NuevaTiendaSerializer(serializers.Serializer):
    """Una tienda nueva con su dueño, en un solo paso."""

    nombre = serializers.CharField(max_length=120)
    slug = serializers.SlugField(
        max_length=60,
        validators=[
            UniqueValidator(
                queryset=Tienda.objects.all(),
                message="Ya hay una tienda con esta dirección.",
            )
        ],
    )
    plan = serializers.ChoiceField(choices=Plan.choices, default=Plan.BASICO)
    plantilla = serializers.ChoiceField(
        choices=Plantilla.choices, default=Plantilla.CLASICA
    )
    duenoNombre = serializers.CharField(max_length=150)
    duenoEmail = serializers.EmailField()
    duenoPassword = serializers.CharField(write_only=True)

    def validate_duenoEmail(self, valor):  # noqa: N802 — nombre del campo
        if Usuario.objects.filter(email__iexact=valor).exists():
            raise serializers.ValidationError("Ya hay una cuenta con este correo.")
        return valor.lower()

    def validate_duenoPassword(self, valor):  # noqa: N802 — nombre del campo
        validate_password(valor)
        return valor


def _tiendas_con_conteos():
    return Tienda.objects.annotate(
        n_productos=Count("productos", distinct=True),
        n_pedidos=Count("pedidos", distinct=True),
        n_usuarios=Count("usuarios", distinct=True),
    ).order_by("nombre")


class TiendasDePlataforma(generics.ListCreateAPIView):
    """GET y POST /plataforma/tiendas."""

    permission_classes = [EsAdminPlataforma]
    serializer_class = TiendaDePlataformaSerializer
    pagination_class = None

    def get_queryset(self):
        return _tiendas_con_conteos()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        datos = NuevaTiendaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        v = datos.validated_data

        tienda = Tienda.objects.create(
            nombre=v["nombre"], slug=v["slug"], plan=v["plan"], plantilla=v["plantilla"]
        )
        Usuario.objects.create_user(
            email=v["duenoEmail"],
            password=v["duenoPassword"],
            nombre=v["duenoNombre"],
            rol=Rol.DUENO_TIENDA,
            tienda=tienda,
        )
        tienda = _tiendas_con_conteos().get(pk=tienda.pk)
        return Response(
            TiendaDePlataformaSerializer(tienda).data, status=status.HTTP_201_CREATED
        )


class TiendaDePlataforma(generics.RetrieveUpdateAPIView):
    """GET y PATCH /plataforma/tiendas/<slug>: plan, plantilla, nombre y estado."""

    permission_classes = [EsAdminPlataforma]
    serializer_class = TiendaDePlataformaSerializer
    lookup_field = "slug"
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return _tiendas_con_conteos()


# ── Solicitudes de acceso ───────────────────────────────────────────────────


class SolicitudDePlataformaSerializer(serializers.ModelSerializer):
    estadoNombre = serializers.CharField(source="get_estado_display", read_only=True)
    fecha = serializers.DateTimeField(source="fecha_creacion", read_only=True)

    class Meta:
        model = SolicitudDeAcceso
        fields = [
            "id",
            "negocio",
            "nombre",
            "email",
            "telefono",
            "mensaje",
            "estado",
            "estadoNombre",
            "notas",
            "fecha",
        ]
        read_only_fields = ["id", "negocio", "nombre", "email", "telefono", "mensaje"]


class SolicitudesDePlataforma(generics.ListAPIView):
    """GET /plataforma/solicitudes: los negocios que pidieron entrar."""

    permission_classes = [EsAdminPlataforma]
    serializer_class = SolicitudDePlataformaSerializer
    pagination_class = None

    def get_queryset(self):
        solicitudes = SolicitudDeAcceso.objects.all()
        estado = self.request.query_params.get("estado")
        if estado in EstadoSolicitud.values:
            solicitudes = solicitudes.filter(estado=estado)
        return solicitudes


class SolicitudDePlataforma(generics.UpdateAPIView):
    """PATCH /plataforma/solicitudes/<id>: estado y notas internas."""

    permission_classes = [EsAdminPlataforma]
    serializer_class = SolicitudDePlataformaSerializer
    queryset = SolicitudDeAcceso.objects.all()
    http_method_names = ["patch"]


# ── Registro de actividad ───────────────────────────────────────────────────


class RegistroSerializer(serializers.ModelSerializer):
    accionNombre = serializers.CharField(source="get_accion_display", read_only=True)
    tienda = serializers.CharField(source="tienda_nombre")
    usuario = serializers.CharField(source="usuario_email")

    class Meta:
        model = Registro
        fields = [
            "id",
            "fecha",
            "tienda",
            "usuario",
            "accion",
            "accionNombre",
            "modelo",
            "objeto",
            "detalle",
            "ip",
        ]


class PaginaDeRegistros(PageNumberPagination):
    page_size = 50
    page_query_param = "pagina"


class RegistrosDePlataforma(generics.ListAPIView):
    """
    GET /plataforma/registros: todo lo que se hizo, lo más nuevo primero.

    Se filtra por tienda (slug), por tipo de acción y por texto libre sobre
    quién, qué y cuál.
    """

    permission_classes = [EsAdminPlataforma]
    serializer_class = RegistroSerializer
    pagination_class = PaginaDeRegistros

    def get_queryset(self):
        registros = Registro.objects.all()
        consulta = self.request.query_params

        if consulta.get("tienda"):
            registros = registros.filter(tienda__slug=consulta["tienda"])
        if consulta.get("accion"):
            registros = registros.filter(accion=consulta["accion"])
        if consulta.get("q"):
            texto = consulta["q"]
            registros = registros.filter(
                Q(usuario_email__icontains=texto)
                | Q(modelo__icontains=texto)
                | Q(objeto__icontains=texto)
            )
        return registros
