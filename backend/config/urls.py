"""
Rutas del proyecto.

Cada app del dominio expone su propio `urls.py` y se monta acá bajo `/api/`.
Las líneas comentadas son el punto de enganche: se descomentan a medida que
cada módulo tenga endpoints.
"""

from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticación por JWT
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Módulos del dominio
    # path("api/tiendas/", include("apps.tiendas.urls")),
    # path("api/catalogo/", include("apps.catalogo.urls")),
    # path("api/precios/", include("apps.precios.urls")),
    # path("api/pedidos/", include("apps.pedidos.urls")),
    # path("api/clientes/", include("apps.clientes.urls")),
    # path("api/ingesta/", include("apps.ingesta.urls")),
    # path("api/analitica/", include("apps.analitica.urls")),
    # path("api/asistente/", include("apps.asistente.urls")),
]
