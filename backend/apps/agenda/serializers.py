"""Serializadores de la agenda."""

from rest_framework import serializers


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
