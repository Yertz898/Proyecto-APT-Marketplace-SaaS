"""Serializadores de la tienda."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.medios import imagen
from apps.core.validadores import validar_imagen
from apps.tiendas.models import Plan, Plantilla, SolicitudDeAcceso, Tienda, Tipografia
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
    pie = serializers.SerializerMethodField()
    aceptaWebpay = serializers.BooleanField(source="acepta_webpay", read_only=True)

    class Meta:
        model = Tienda
        fields = [
            "slug",
            "nombre",
            "logo",
            "banner",
            "colores",
            "redes",
            "pie",
            "aceptaWebpay",
            "plantilla",
        ]

    def get_logo(self, tienda):
        return imagen(tienda.logo, tienda.nombre)

    def get_banner(self, tienda):
        return imagen(tienda.banner, tienda.nombre)

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

    def get_pie(self, tienda):
        return {
            "descripcion": tienda.pie_descripcion,
            "correo": tienda.pie_correo,
            "telefono": tienda.pie_telefono,
            "direccion": tienda.pie_direccion,
            "horario": tienda.pie_horario,
            "redes": list(tienda.redes_sociales or []),
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
#: El pie de página viene con todos los planes: es información de contacto,
#: no marca.
CAMPOS_DEL_PIE = {
    "pie_descripcion",
    "pie_correo",
    "pie_telefono",
    "pie_direccion",
    "pie_horario",
    "redes_sociales",
}
CAMPOS_DEL_PLAN_BASICO = {
    "nombre",
    "logo",
    "plantilla",
    "acepta_webpay",
} | CAMPOS_DEL_PIE

#: Cuántos enlaces a redes acepta el pie.
MAXIMO_DE_REDES = 8


class ListaDeRedes(serializers.Field):
    """
    Los enlaces a redes sociales del pie.

    El perfil se guarda como multipart (lleva el logo y el banner), y en un
    formulario una lista viaja como texto JSON: se aceptan las dos formas. Cada
    enlace tiene que ser https, porque termina en el href de la vitrina.
    """

    def to_representation(self, valor):
        return list(valor or [])

    def to_internal_value(self, datos):
        import json

        if isinstance(datos, str):
            try:
                datos = json.loads(datos) if datos.strip() else []
            except ValueError:
                raise serializers.ValidationError(
                    "No es una lista de enlaces."
                ) from None
        if not isinstance(datos, list):
            raise serializers.ValidationError("No es una lista de enlaces.")

        validador = URLValidator(schemes=["https"])
        enlaces = []
        for crudo in datos:
            enlace = str(crudo).strip()
            if not enlace:
                continue
            try:
                validador(enlace)
            except DjangoValidationError:
                raise serializers.ValidationError(
                    f"«{enlace[:60]}» no es un enlace válido: tiene que empezar con https://."
                ) from None
            if enlace not in enlaces:
                enlaces.append(enlace)
        if len(enlaces) > MAXIMO_DE_REDES:
            raise serializers.ValidationError(
                f"Puedes poner hasta {MAXIMO_DE_REDES} redes sociales."
            )
        return enlaces


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
    plantillasDisponibles = serializers.SerializerMethodField()
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
    pieDescripcion = serializers.CharField(
        source="pie_descripcion", required=False, allow_blank=True, max_length=300
    )
    pieCorreo = serializers.EmailField(
        source="pie_correo", required=False, allow_blank=True
    )
    pieTelefono = serializers.CharField(
        source="pie_telefono", required=False, allow_blank=True, max_length=30
    )
    pieDireccion = serializers.CharField(
        source="pie_direccion", required=False, allow_blank=True, max_length=200
    )
    pieHorario = serializers.CharField(
        source="pie_horario", required=False, allow_blank=True, max_length=120
    )
    redesSociales = ListaDeRedes(source="redes_sociales", required=False)
    aceptaWebpay = serializers.BooleanField(source="acepta_webpay", required=False)

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
            "pieDescripcion",
            "pieCorreo",
            "pieTelefono",
            "pieDireccion",
            "pieHorario",
            "redesSociales",
            "aceptaWebpay",
            "tipografiasDisponibles",
            "plantilla",
            "plantillasDisponibles",
            "puedeEditarLaMarca",
        ]
        read_only_fields = ["slug", "plan"]

    def get_logoActual(self, tienda):
        return imagen(tienda.logo, tienda.nombre)

    def get_bannerActual(self, tienda):
        return imagen(tienda.banner, tienda.nombre)

    def get_tipografiasDisponibles(self, tienda):
        # La lista viaja con el perfil para que el panel no la repita: si mañana
        # se agrega una fuente, el selector la muestra sin tocar el frontend.
        return [{"valor": v, "nombre": n} for v, n in Tipografia.choices]

    def get_plantillasDisponibles(self, tienda):
        return [{"valor": v, "nombre": n} for v, n in Plantilla.choices]

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
