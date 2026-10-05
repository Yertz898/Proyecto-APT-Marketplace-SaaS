"""
Vistas del catálogo público.

Todo lo de acá cuelga de `/t/<slug>/`, que es la vitrina: la tienda sale de la
ruta y solo se exponen datos publicados. El filtro por tienda lo aplica
`MixinTiendaPublica`, no cada vista: repetirlo a mano es cómo se olvida en la
siguiente.

Un producto de otra tienda, inactivo o agotado responde 404 y no 403. Un 403
confirmaría que ese código existe en alguna parte, y los códigos viajan en la
URL.
"""

from decimal import Decimal, InvalidOperation

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.models import FormaVenta, Producto
from apps.catalogo.serializers import CotizacionSerializer, ProductoSerializer
from apps.catalogo.serializers_panel import (
    ProductoDelPanelSerializer,
    ResumenDeInventarioSerializer,
)
from apps.core.mixins import MixinTiendaDelUsuario, MixinTiendaPublica
from apps.core.permissions import TrabajaEnLaTienda
from apps.precios.servicios import cotizar


class PaginaDeProductos(PageNumberPagination):
    """
    Paginación con la forma que espera el frontend.

    DRF entrega `count`, `next` y `previous`; la vitrina trabaja con el número
    de página y el total de páginas, que es lo que dibuja su paginador.
    """

    page_size = 12
    page_query_param = "pagina"
    max_page_size = 48

    def get_paginated_response(self, data):
        return Response(
            {
                "productos": data,
                "paginaActual": self.page.number,
                "totalPaginas": self.page.paginator.num_pages,
            }
        )


class VitrinaMixin(MixinTiendaPublica):
    """
    La vitrina es pública y no mira el token.

    `parametro_slug` es el nombre que la ruta le da a la tienda; el mixin lo
    usa para resolverla y acotar el queryset a lo publicado.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    parametro_slug = "slug"


class CatalogoMixin(VitrinaMixin):
    """Productos publicados de la tienda, con lo que el serializador va a leer."""

    queryset = Producto.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("categoria")
            .prefetch_related("composicion__categoria", "tramos")
        )


class ListaDeProductos(CatalogoMixin, generics.ListAPIView):
    serializer_class = ProductoSerializer
    pagination_class = PaginaDeProductos

    def get_queryset(self):
        productos = super().get_queryset()

        forma = self.request.query_params.get("forma")
        if forma:
            # Una forma que no existe devuelve vacío y no 400: viene de la URL
            # y un enlace viejo no debería reventar la vitrina.
            productos = productos.filter(forma_venta=forma)

        categoria = self.request.query_params.get("categoria")
        if categoria:
            productos = productos.filter(categoria__nombre=categoria)

        return productos


class DetalleDeProducto(CatalogoMixin, generics.RetrieveAPIView):
    serializer_class = ProductoSerializer
    lookup_field = "codigo"


class FormasDeVenta(VitrinaMixin, APIView):
    """
    Cómo vende esta tienda.

    La vitrina arma sus pestañas con esto y no con una lista escrita en el
    frontend: una tienda que solo vende por unidad no muestra ninguna pestaña,
    y otra que mañana agregue venta por peso la muestra sin tocar código.
    """

    def get(self, request, slug):
        tienda = self.get_tienda()
        usadas = set(
            Producto.objects.publicadas_de(tienda)
            .values_list("forma_venta", flat=True)
            .distinct()
        )
        return Response(
            [
                {"valor": valor, "nombre": nombre}
                for valor, nombre in FormaVenta.choices
                if valor in usadas
            ]
        )


class CotizarProducto(CatalogoMixin, generics.GenericAPIView):
    """
    Qué cuesta llevar una cantidad de un producto.

    Un rechazo —bajo el mínimo, sin stock— responde 200 con el motivo adentro,
    no 400: la petición está bien hecha y la vitrina necesita mostrar la razón
    donde corresponde, no un error.
    """

    serializer_class = CotizacionSerializer
    lookup_field = "codigo"

    def post(self, request, slug, codigo):
        producto = self.get_object()
        cantidad = self._cantidad(request.data.get("cantidad"))
        return Response(CotizacionSerializer(cotizar(producto, cantidad)).data)

    def _cantidad(self, valor) -> Decimal:
        try:
            cantidad = Decimal(str(valor))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError(
                {"cantidad": "Escribe una cantidad válida."}
            ) from None

        if cantidad <= 0:
            raise ValidationError(
                {"cantidad": "La cantidad tiene que ser mayor que 0."}
            )

        return cantidad


# ── El catálogo desde el panel ──────────────────────────────────────────────


class PaginaDelPanel(PageNumberPagination):
    page_size = 25
    page_query_param = "pagina"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "productos": data,
                "paginaActual": self.page.number,
                "totalPaginas": self.page.paginator.num_pages,
            }
        )


class CatalogoDelPanel(MixinTiendaDelUsuario, generics.ListAPIView):
    """
    Los productos de la tienda del usuario, como los ve su dueño.

    No es el mismo listado que la vitrina: acá aparece lo desactivado y lo
    agotado, que es justamente lo que pide atención. La tienda sale del token,
    así que no hay forma de pedir el catálogo de otra.
    """

    serializer_class = ProductoDelPanelSerializer
    pagination_class = PaginaDelPanel
    permission_classes = [TrabajaEnLaTienda]
    queryset = Producto.objects.all()

    #: Primero lo que pide atención. Un `estado` calculado no se puede ordenar
    #: en SQL, así que se ordena por lo que lo compone.
    ORDEN = ["activo", "-controla_stock", "stock", "codigo"]

    def get_queryset(self):
        productos = (
            super().get_queryset().select_related("categoria").prefetch_related("tramos")
        )

        forma = self.request.query_params.get("forma")
        if forma:
            productos = productos.filter(forma_venta=forma)

        return productos.order_by(*self.ORDEN)


class InventarioDelPanel(MixinTiendaDelUsuario, generics.GenericAPIView):
    """
    Cuántos productos están en cada situación.

    Son hechos, no predicciones: cuántos se publicaron, cuántos se
    desactivaron, cuántos se agotaron y a cuántos les queda una unidad. La
    alerta por demanda proyectada es otra cosa y necesita el pronóstico, que
    todavía no existe; inventarla acá sería mostrar un número sin respaldo.
    """

    serializer_class = ResumenDeInventarioSerializer
    permission_classes = [TrabajaEnLaTienda]
    queryset = Producto.objects.all()

    def get(self, request):
        productos = self.get_queryset()
        con_stock = productos.filter(controla_stock=True)

        return Response(
            ResumenDeInventarioSerializer(
                {
                    "publicados": productos.filter(activo=True).count(),
                    "desactivados": productos.filter(activo=False).count(),
                    "agotados": con_stock.filter(activo=True, stock__lte=0).count(),
                    "ultimaUnidad": con_stock.filter(activo=True, stock=1).count(),
                }
            ).data
        )
