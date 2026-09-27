"""Serializadores de la tienda."""

from rest_framework import serializers

from apps.tiendas.models import Tienda


class TiendaPublicaSerializer(serializers.ModelSerializer):
    """
    Identidad de la tienda para su vitrina pública.

    Solo expone lo que el comprador necesita ver. No incluye nada de
    administración ni datos de otras tiendas.

    Las claves compuestas van en camelCase porque este contrato lo consume el
    frontend, que ya está escrito así.
    """

    logo = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    colores = serializers.SerializerMethodField()
    redes = serializers.SerializerMethodField()

    class Meta:
        model = Tienda
        fields = ["slug", "nombre", "logo", "banner", "colores", "redes"]

    def _imagen(self, archivo, alt):
        if not archivo:
            return None

        url = archivo.url
        peticion = self.context.get("request")
        if peticion is not None:
            url = peticion.build_absolute_uri(url)

        return {"url": url, "alt": alt}

    def get_logo(self, tienda):
        return self._imagen(tienda.logo, tienda.nombre)

    def get_banner(self, tienda):
        return self._imagen(tienda.banner, tienda.nombre)

    def get_colores(self, tienda):
        # Todo o nada: si la tienda no definió su paleta completa, el frontend
        # usa la de la plataforma en vez de mezclar colores a medias.
        colores = {
            "primario": tienda.color_primario,
            "primarioHover": tienda.color_primario_hover,
            "acento": tienda.color_acento,
            "destacado": tienda.color_destacado,
        }
        return colores if all(colores.values()) else None

    def get_redes(self, tienda):
        return {
            "whatsapp": tienda.whatsapp or None,
            "instagram": tienda.instagram or None,
        }
