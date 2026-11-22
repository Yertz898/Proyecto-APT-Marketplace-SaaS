"""Serializadores de la agenda."""

import re

from rest_framework import serializers

from apps.agenda.models import Visita

#: Letras de cualquier idioma, espacios, apóstrofo, punto y guion.
NOMBRE = re.compile(r"[^\W\d_]+(?:[ '.\-][^\W\d_]+)*\.?")
#: Celular chileno con su prefijo: +569 y ocho dígitos.
CELULAR = re.compile(r"\+569\d{8}")


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

    def validate_nombreContacto(self, valor):  # noqa: N802 — nombre del campo
        """Un nombre: letras, espacios, apóstrofo y guion. Sin números."""
        valor = " ".join(valor.split())
        if not NOMBRE.fullmatch(valor):
            raise serializers.ValidationError("Escribe tu nombre solo con letras.")
        return valor

    def validate_telefonoContacto(self, valor):  # noqa: N802 — nombre del campo
        """
        Un celular chileno: +569 y ocho dígitos.

        Se aceptan espacios y guiones al escribirlo, pero se guarda junto, que
        es como lo entiende WhatsApp.
        """
        numero = re.sub(r"[\s-]", "", valor)
        if not CELULAR.fullmatch(numero):
            raise serializers.ValidationError(
                "El teléfono tiene que ser un celular: +569 y 8 dígitos."
            )
        return numero


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


class MiVisitaSerializer(serializers.ModelSerializer):
    """
    Una visita en «Mis citas» del comprador.

    Trae el cambio de hora pendiente, si hay, y qué puede hacer con la visita:
    reagendar, cancelar y responder la propuesta de la tienda.
    """

    estadoNombre = serializers.CharField(source="get_estado_display", read_only=True)
    motivoRechazo = serializers.CharField(source="motivo_rechazo", read_only=True)
    cambioPendiente = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()

    class Meta:
        model = Visita
        fields = [
            "id",
            "inicio",
            "fin",
            "estado",
            "estadoNombre",
            "motivo",
            "motivoRechazo",
            "cambioPendiente",
            "vigente",
        ]
        read_only_fields = fields

    def get_cambioPendiente(self, visita):  # noqa: N802 — nombre del campo
        from apps.agenda import cambios

        return cambios.representar(cambios.pendiente_de(visita))

    def get_vigente(self, visita):
        from apps.agenda.models import ESTADOS_VIGENTES

        return visita.estado in ESTADOS_VIGENTES
