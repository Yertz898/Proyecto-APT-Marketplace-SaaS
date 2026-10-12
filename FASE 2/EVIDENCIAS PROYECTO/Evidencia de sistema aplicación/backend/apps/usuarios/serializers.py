"""
Serializadores de cuentas y sesión.

El contrato lo consume el frontend, así que las claves compuestas van en
camelCase, igual que en el resto de la API.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.usuarios.models import Rol, Usuario
from apps.usuarios.validadores import normalizar_rut, validar_rut


class TiendaDeLaSesionSerializer(serializers.Serializer):
    """Lo mínimo para que el panel sepa en qué tienda está parado."""

    slug = serializers.SlugField(read_only=True)
    nombre = serializers.CharField(read_only=True)


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Quién es el usuario de la sesión.

    No expone la contraseña ni los permisos de Django: el frontend decide qué
    dibujar, no qué se puede hacer. Lo que se puede hacer lo resuelve el backend
    en cada endpoint.
    """

    tienda = TiendaDeLaSesionSerializer(read_only=True)
    rolNombre = serializers.CharField(source="get_rol_display", read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "email", "rol", "rolNombre", "tienda"]
        read_only_fields = fields


class TokenDeSesionSerializer(TokenObtainPairSerializer):
    """
    Inicio de sesión: entrega los dos tokens y de paso quién inició sesión.

    El rol y la tienda viajan también dentro del token, pero solo para que el
    frontend pueda dibujar sin una segunda llamada. La autorización no los lee
    de ahí: en cada petición el backend vuelve a cargar al usuario desde la base
    de datos, así un cambio de rol o una cuenta desactivada surten efecto sin
    esperar a que venza el token.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.rol
        token["tienda"] = user.tienda.slug if user.tienda_id else None
        return token

    def validate(self, attrs):
        datos = super().validate(attrs)
        datos["usuario"] = UsuarioSerializer(self.user).data
        return datos


class RegistroCompradorSerializer(serializers.ModelSerializer):
    """
    Alta de un comprador.

    `rol` y `tienda` no son campos a propósito: quien se registra queda siempre
    como comprador sin tienda, mande lo que mande en el cuerpo. Las cuentas de
    dueño y de vendedor las crea la tienda, y la de administrador no se crea
    desde la interfaz.
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

    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, label="contraseña"
    )

    rut = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Usuario
        fields = ["nombre", "email", "rut", "password"]

    def validate_password(self, valor):
        """Las reglas son las de Django: largo mínimo, no común, no solo dígitos."""
        validate_password(valor)
        return valor

    def validate_rut(self, valor):
        if not valor:
            return ""

        validar_rut(valor)
        rut = normalizar_rut(valor)

        # El RUT se compara normalizado: "12.345.678-5" y "12345678-5" son el
        # mismo y la restricción de unicidad no lo sabría.
        if Usuario.objects.filter(rut=rut).exists():
            raise serializers.ValidationError("Ya hay una cuenta con este RUT.")

        return rut

    def create(self, datos):
        return Usuario.objects.create_user(
            email=datos["email"],
            password=datos["password"],
            nombre=datos["nombre"],
            # Vacío es «no lo dio», y eso es nulo: dos cuentas con el RUT en
            # blanco chocarían contra la restricción de unicidad.
            rut=datos.get("rut") or None,
            rol=Rol.COMPRADOR,
        )
