"""
Rutas del proyecto.

Cada app del dominio expone su propio `urls.py` y se monta acá bajo `/api/`.
Las líneas comentadas son el punto de enganche: se descomentan a medida que
cada módulo tenga endpoints.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Sesión y cuentas
    path("api/", include("apps.usuarios.urls")),
    # Módulos del dominio
    path("api/", include("apps.tiendas.urls")),
    path("api/", include("apps.agenda.urls")),
    # path("api/catalogo/", include("apps.catalogo.urls")),
    # path("api/precios/", include("apps.precios.urls")),
    # path("api/pedidos/", include("apps.pedidos.urls")),
    # path("api/clientes/", include("apps.clientes.urls")),
    # path("api/ingesta/", include("apps.ingesta.urls")),
    # path("api/analitica/", include("apps.analitica.urls")),
    # path("api/asistente/", include("apps.asistente.urls")),
]

# En desarrollo las imágenes se guardan en disco y las sirve el mismo Django.
# En producción las sirve Cloudflare R2 y esto no aplica.
if settings.DEBUG and hasattr(settings, "MEDIA_URL"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
