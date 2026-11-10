"""Serializadores de la carga masiva."""

from rest_framework import serializers

from apps.ingesta.models import Carga


class CargaDelHistorialSerializer(serializers.ModelSerializer):
    """
    Una línea del historial.

    `resultado` lo redacta el backend y no el navegador: el frontend muestra
    texto, no arma frases con cifras que podría leer al revés.
    """

    id = serializers.CharField(read_only=True)
    fecha = serializers.DateTimeField(source="fecha_creacion", read_only=True)
    usuario = serializers.CharField(source="usuario.nombre", read_only=True)
    archivo = serializers.CharField(source="nombre_original", read_only=True)
    resultado = serializers.CharField(read_only=True)

    class Meta:
        model = Carga
        fields = ["id", "tipo", "fecha", "usuario", "archivo", "resultado"]
