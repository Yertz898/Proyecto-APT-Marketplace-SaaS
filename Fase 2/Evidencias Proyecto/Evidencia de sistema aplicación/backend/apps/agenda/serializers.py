"""Serializadores de la agenda."""

from rest_framework import serializers

from apps.agenda.models import Visita


class HoraDisponibleSerializer(serializers.Serializer):
    """
    Una hora que el comprador puede elegir.

    Las claves compuestas van en camelCase porque este contrato lo consume el
    frontend, igual que el de la identidad de la tienda.
    """

    inicio = serializers.DateTimeField(read_only=True)
    fin = serializers.DateTimeField(read_only=True)
    bloqueId = serializers.IntegerField(source="bloque_id", read_only=True)
    nombreBloque = serializers.CharField(source="nombre_bloque", read_only=True)
    cuposLibres = serializers.IntegerField(source="cupos_libres", read_only=True)
    confirmacionAutomatica = serializers.BooleanField(
        source="confirmacion_automatica", read_only=True
    )


class SolicitudDeVisitaSerializer(serializers.Serializer):
    """
    Lo que manda el comprador para pedir una hora.

    No se pide la tienda ni el comprador: la tienda sale del slug de la ruta y
    el comprador del token. Mandarlos en el cuerpo no serviría de nada.

    Tampoco se pide el término de la visita: lo determina la duración del bloque
    y no el navegador.
    """

    inicio = serializers.DateTimeField()
    nombreContacto = serializers.CharField(source="nombre_contacto", max_length=150)
    correoContacto = serializers.EmailField(source="correo_contacto")
    telefonoContacto = serializers.CharField(source="telefono_contacto", max_length=30)
    motivo = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class VisitaSerializer(serializers.ModelSerializer):
    """La visita como la ve el comprador que la acaba de pedir."""

    estadoNombre = serializers.CharField(source="get_estado_display", read_only=True)
    nombreContacto = serializers.CharField(source="nombre_contacto", read_only=True)
    correoContacto = serializers.EmailField(source="correo_contacto", read_only=True)
    telefonoContacto = serializers.CharField(source="telefono_contacto", read_only=True)

    class Meta:
        model = Visita
        fields = [
            "uid",
            "inicio",
            "fin",
            "estado",
            "estadoNombre",
            "nombreContacto",
            "correoContacto",
            "telefonoContacto",
            "motivo",
        ]
        read_only_fields = fields
