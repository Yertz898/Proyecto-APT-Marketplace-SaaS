"""Serializadores de la tienda."""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.validadores import validar_imagen
from apps.tiendas.models import Plan, SolicitudDeAcceso, Tienda, Tipografia
from apps.tiendas.validadores import validar_color_hexadecimal


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


class SolicitudDeAccesoSerializer(serializers.ModelSerializer):
    """
    Lo que escribe un negocio en la portada para pedir entrar.

    `estado` y `notas` no son campos: los maneja el equipo desde el panel de
    administración. Mandarlos en el cuerpo no sirve de nada.
    """

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=SolicitudDeAcceso.objects.all(),
                lookup="iexact",
                message=(
                    "Ya recibimos una solicitud con este correo. Te vamos a escribir."
                ),
            )
        ]
    )

    class Meta:
        model = SolicitudDeAcceso
        fields = ["negocio", "nombre", "email", "telefono", "mensaje"]

    def create(self, datos):
        datos["email"] = datos["email"].lower()
        return super().create(datos)


#: Lo que el plan Básico deja tocar del perfil.
#:
#: El resto de la marca —banner, colores, tipografía y redes— viene con Premium.
#: La decisión es del backend, igual que con los roles: la interfaz dibuja el
#: candado, pero un candado de interfaz no protege nada.
CAMPOS_DEL_PLAN_BASICO = {"nombre", "logo"}


def _color(campo):
    """Un color de la paleta, con el mismo validador que el modelo."""
    return serializers.CharField(
        source=campo,
        max_length=7,
        required=False,
        allow_blank=True,
        validators=[validar_color_hexadecimal],
    )


class PerfilDeTiendaSerializer(serializers.ModelSerializer):
    """
    El perfil de la tienda como lo ve y lo edita su panel.

    No recibe `slug` ni `plan`: el primero es la dirección pública y cambiarlo
    rompería los enlaces que la tienda ya repartió; el segundo lo administra la
    plataforma, no la tienda.

    Las imágenes se devuelven como objeto y se reciben como archivo, igual que
    en la vitrina pública: el frontend ya lee `{url, alt}`.
    """

    logoActual = serializers.SerializerMethodField()
    bannerActual = serializers.SerializerMethodField()
    tipografiasDisponibles = serializers.SerializerMethodField()
    puedeEditarLaMarca = serializers.SerializerMethodField()

    logo = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
        validators=[validar_imagen],
    )
    banner = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
        validators=[validar_imagen],
    )

    # Declarados a mano para que el contrato vaya en camelCase, así que los
    # validadores del modelo hay que repetirlos: al declarar el campo, DRF ya no
    # los hereda. Dejar pasar un color sin validar sería CSS de una tienda
    # corriendo en la página de otra.
    colorPrimario = _color("color_primario")
    colorPrimarioHover = _color("color_primario_hover")
    colorAcento = _color("color_acento")
    colorDestacado = _color("color_destacado")

    class Meta:
        model = Tienda
        fields = [
            "slug",
            "nombre",
            "plan",
            "logo",
            "banner",
            "logoActual",
            "bannerActual",
            "colorPrimario",
            "colorPrimarioHover",
            "colorAcento",
            "colorDestacado",
            "tipografia",
            "whatsapp",
            "instagram",
            "tipografiasDisponibles",
            "puedeEditarLaMarca",
        ]
        read_only_fields = ["slug", "plan"]

    def _imagen(self, archivo, alt):
        if not archivo:
            return None

        url = archivo.url
        peticion = self.context.get("request")
        if peticion is not None:
            url = peticion.build_absolute_uri(url)

        return {"url": url, "alt": alt}

    def get_logoActual(self, tienda):
        return self._imagen(tienda.logo, tienda.nombre)

    def get_bannerActual(self, tienda):
        return self._imagen(tienda.banner, tienda.nombre)

    def get_tipografiasDisponibles(self, tienda):
        # La lista viaja con el perfil para que el panel no la repita: si mañana
        # se agrega una fuente, el selector la muestra sin tocar el frontend.
        return [{"valor": v, "nombre": n} for v, n in Tipografia.choices]

    def get_puedeEditarLaMarca(self, tienda):
        return tienda.plan != Plan.BASICO

    def validate(self, datos):
        tienda = self.instance
        if tienda is None or tienda.plan != Plan.BASICO:
            return datos

        # `datos` ya viene con los nombres del modelo, no con los del contrato.
        bloqueados = sorted(set(datos) - CAMPOS_DEL_PLAN_BASICO)
        if bloqueados:
            raise serializers.ValidationError(
                {
                    campo: serializers.ErrorDetail(
                        "Esta parte de la marca viene con el plan Premium.",
                        code="requiere_plan",
                    )
                    for campo in bloqueados
                }
            )

        return datos
