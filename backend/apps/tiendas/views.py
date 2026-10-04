"""Vistas de la API de `tiendas`."""

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

from apps.core.permissions import EsDuenoDeTienda, TrabajaEnLaTienda
from apps.tiendas.models import Tienda
from apps.tiendas.serializers import (
    PerfilDeTiendaSerializer,
    SolicitudDeAccesoSerializer,
    TiendaPublicaSerializer,
)


class TiendaPublica(generics.RetrieveAPIView):
    """
    Identidad de una tienda para su vitrina pública.

    Va sin sesión, porque la vitrina la ve cualquiera.
    La tienda se resuelve por el slug de la ruta, que es lo que corresponde para
    el catálogo público (CONVENCIONES.md > Cómo se resuelve la tienda en cada
    petición). Todo lo demás sigue sacando la tienda del token.

    Una tienda inactiva o inexistente responde 404, sin distinguir entre las dos
    cosas: decir cuál es cuál confirmaría qué slugs existen.
    """

    serializer_class = TiendaPublicaSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    lookup_field = "slug"
    queryset = Tienda.objects.filter(activa=True)


class PedirAcceso(generics.CreateAPIView):
    """
    Solicitud de acceso a la plataforma, desde la portada.

    Es un formulario público, así que lo puede enviar cualquiera desde
    internet: lleva límite de frecuencia por IP para que no se convierta en una
    forma barata de llenar la bandeja del equipo.

    No responde nada que la persona no haya escrito ella misma. En particular,
    un correo repetido devuelve un mensaje de recibo y no la invitación a
    averiguar qué negocios ya pidieron entrar.
    """

    serializer_class = SolicitudDeAccesoSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "solicitudes"


class PerfilDeTienda(generics.RetrieveUpdateAPIView):
    """
    El perfil de la tienda propia, desde el panel.

    No hay identificador en la ruta, y no es un descuido: la tienda sale del
    token y de ninguna otra parte (CONVENCIONES.md > Cómo se resuelve la tienda
    en cada petición). Sin un `id` que forzar, no existe la petición que pida el
    perfil de otra tienda.

    Leer lo puede el dueño o un vendedor; escribir, solo el dueño. Al vendedor
    se le responde 403 y no 404: no se le está escondiendo nada, es su propia
    tienda y la ve igual.
    """

    serializer_class = PerfilDeTiendaSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [TrabajaEnLaTienda()]
        return [EsDuenoDeTienda()]

    def get_object(self):
        return self.request.user.tienda
