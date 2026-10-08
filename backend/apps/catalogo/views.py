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

from django.utils.functional import cached_property
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.models import Categoria, FormaVenta, Producto
from apps.catalogo.serializers import CotizacionSerializer, ProductoSerializer
from apps.catalogo.serializers_panel import (
    CategoriaSerializer,
    EdicionDeProductoSerializer,
    ProductoDelPanelSerializer,
    ResumenDeInventarioSerializer,
)
from apps.catalogo.serializers_panel import (
    TramoSerializer as TramoDelPanelSerializer,
)
from apps.core.mixins import MixinTiendaDelUsuario, MixinTiendaPublica
from apps.core.permissions import TrabajaEnLaTienda
from apps.precios.models import TramoPrecio
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


class CatalogoDelPanel(MixinTiendaDelUsuario, generics.ListCreateAPIView):
    """
    Los productos de la tienda del usuario, como los ve su dueño.

    No es el mismo listado que la vitrina: acá aparece lo desactivado y lo
    agotado, que es justamente lo que pide atención. La tienda sale del token,
    así que no hay forma de pedir el catálogo de otra.
    """

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

    def get_serializer_class(self):
        # Listar y crear no son el mismo contrato: uno devuelve el estado
        # calculado y el otro recibe los campos del modelo.
        if self.request.method == "POST":
            return EdicionDeProductoSerializer
        return ProductoDelPanelSerializer

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "tienda": self.request.user.tienda}

    def create(self, request, *args, **kwargs):
        serializador = self.get_serializer(data=request.data)
        serializador.is_valid(raise_exception=True)
        producto = serializador.save()

        # Se responde con la forma del listado, que es la que la pantalla ya
        # sabe dibujar.
        return Response(
            ProductoDelPanelSerializer(producto).data, status=status.HTTP_201_CREATED
        )


class ProductoDelPanel(MixinTiendaDelUsuario, generics.RetrieveUpdateAPIView):
    """
    Un producto de la tienda propia: leerlo y editarlo.

    **No hay DELETE, y es deliberado**: en este proyecto el catálogo nunca se
    borra, se desactiva (`activo`). Un producto borrado se lleva por delante su
    composición, sus tramos y, cuando existan, las líneas de pedidos que lo
    nombran. Desactivar lo saca de la vitrina y conserva el historial.

    Un código de otra tienda responde 404 y no 403: el código viaja en la URL,
    así que es adivinable, y un 403 confirmaría que existe en alguna parte.
    """

    permission_classes = [TrabajaEnLaTienda]
    queryset = Producto.objects.all()
    lookup_field = "codigo"
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return EdicionDeProductoSerializer
        return ProductoDelPanelSerializer

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "tienda": self.request.user.tienda}

    def update(self, request, *args, **kwargs):
        producto = self.get_object()
        serializador = self.get_serializer(producto, data=request.data, partial=True)
        serializador.is_valid(raise_exception=True)
        serializador.save()

        producto.refresh_from_db()
        return Response(ProductoDelPanelSerializer(producto).data)


class CategoriasDelPanel(MixinTiendaDelUsuario, generics.ListCreateAPIView):
    """Las categorías de la tienda. Las usa el catálogo y el pronóstico."""

    serializer_class = CategoriaSerializer
    permission_classes = [TrabajaEnLaTienda]
    pagination_class = None
    queryset = Categoria.objects.all()

    def perform_create(self, serializer):
        serializer.save(tienda=self.request.user.tienda)


class CategoriaDelPanel(MixinTiendaDelUsuario, generics.RetrieveUpdateDestroyAPIView):
    """
    Una categoría.

    Borrarla sí se permite, al revés que con los productos: una categoría no
    guarda historial. Pero si algún producto la usa, la base lo impide
    (PROTECT) y acá se traduce a un mensaje que dice por qué.
    """

    serializer_class = CategoriaSerializer
    permission_classes = [TrabajaEnLaTienda]
    queryset = Categoria.objects.all()

    def perform_destroy(self, categoria):
        if categoria.productos.exists():
            raise ValidationError(
                {
                    "categoria": "Hay productos en esta categoría. Cámbialos de "
                    "categoría antes de borrarla."
                }
            )
        categoria.delete()


class TramosDelProducto(MixinTiendaDelUsuario, generics.ListCreateAPIView):
    """
    Los tramos de precio de un producto.

    Cuelgan del producto y no de la tienda: un precio por volumen es del
    producto que se vende. Acá no hay descuentos.
    """

    serializer_class = TramoDelPanelSerializer
    permission_classes = [TrabajaEnLaTienda]
    pagination_class = None
    queryset = TramoPrecio.objects.all()

    def get_queryset(self):
        # `super()` es el mixin, que ya acotó a la tienda del token. Partir de
        # TramoPrecio.objects directamente dejaría fuera ese filtro.
        return super().get_queryset().filter(producto=self.producto)

    @cached_property
    def producto(self):
        """El producto de la ruta, buscado dentro de la tienda del usuario."""
        return generics.get_object_or_404(
            Producto.objects.de_usuario(self.request.user),
            codigo=self.kwargs["codigo"],
        )

    def get_serializer_context(self):
        # El serializador necesita el producto para ver si el umbral se repite.
        # Sin esto, el duplicado llega a la base y vuelve como un 500.
        return {**super().get_serializer_context(), "producto": self.producto}

    def perform_create(self, serializer):
        serializer.save(tienda=self.request.user.tienda, producto=self.producto)


class TramoDelPanel(MixinTiendaDelUsuario, generics.RetrieveUpdateDestroyAPIView):
    """
    Un tramo. Borrarlo no pierde historial: es solo una regla de precio.

    El queryset se declara como atributo y **no se sobrescribe**: el mixin lo
    acota a la tienda del token. Sobrescribir `get_queryset` acá fue, durante
    un rato, una fuga por la que se podía borrar el tramo de otra tienda.
    """

    serializer_class = TramoDelPanelSerializer
    permission_classes = [TrabajaEnLaTienda]
    queryset = TramoPrecio.objects.all()


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
