"""
Mixins de vista que aplican el filtro por tienda de forma automática.

Las vistas del resto de las apps heredan de acá en vez de repetir el filtro a
mano. Una vista que arma su queryset por su cuenta se salta el invariante.
"""

from rest_framework.exceptions import NotFound


class MixinTiendaDelUsuario:
    """
    Acota el queryset a la tienda del usuario autenticado.

    La tienda sale del usuario, que sale del token. Un `tienda_id` que llegue en
    el cuerpo o en la query string no se confía nunca (CLAUDE.md > Cómo se
    resuelve la tienda en cada petición).

    Al no encontrar el recurso, DRF responde 404 y no 403: un 403 confirmaría
    que el recurso existe en otra tienda.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.de_usuario(self.request.user)

    def perform_create(self, serializer):
        """
        La tienda del objeto nuevo es la del usuario, nunca la que venga en el
        cuerpo de la petición.
        """
        usuario = self.request.user
        if not getattr(usuario, "trabaja_en_tienda", False) or not usuario.tienda_id:
            raise NotFound()
        serializer.save(tienda_id=usuario.tienda_id)


class MixinTiendaPublica:
    """
    Acota el queryset a la tienda de la ruta pública /t/<slug>/.

    Solo expone datos publicados y no depende de que haya sesión: es la vitrina
    que ve cualquier comprador.
    """

    #: Nombre del parámetro de la URL que trae el slug de la tienda.
    parametro_slug = "slug_tienda"

    def get_tienda(self):
        from apps.tiendas.models import Tienda

        slug = self.kwargs.get(self.parametro_slug)
        try:
            return Tienda.objects.get(slug=slug, activa=True)
        except Tienda.DoesNotExist:
            # 404 y no 403: un 403 confirmaría que la tienda existe.
            raise NotFound() from None

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.publicadas_de(self.get_tienda())
