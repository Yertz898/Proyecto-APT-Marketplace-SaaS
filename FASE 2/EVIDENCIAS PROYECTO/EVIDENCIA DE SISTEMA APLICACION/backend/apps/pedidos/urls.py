from django.urls import path

from apps.pedidos.views import (
    ConfirmarPedidoView,
    CotizarCarritoView,
    PedidoPanelEstadoView,
    PedidoPanelListView,
)

urlpatterns = [
    # ── Vitrina pública (Comprador) ──────────────────────────────────────
    # Cotización en tiempo real (totales, IVA y tramos de precio)
    path(
        "t/<slug:slug>/carrito/cotizar",
        CotizarCarritoView.as_view(),
        name="carrito-cotizar",
    ),
    path("t/<slug:slug>/carrito/cotizar/", CotizarCarritoView.as_view()),
    # Confirmación de pedido con checkout simulado y reserva de stock
    path(
        "t/<slug:slug>/pedidos", ConfirmarPedidoView.as_view(), name="pedido-confirmar"
    ),
    path("t/<slug:slug>/pedidos/", ConfirmarPedidoView.as_view()),
    # ── Panel administrativo (Vendedor / Dueño) ──────────────────────────
    # Bandeja de pedidos de la tienda
    path("panel/pedidos/", PedidoPanelListView.as_view(), name="panel-pedidos-lista"),
    # Actualización de estados (confirmar, entregar o anular devolviendo stock)
    path(
        "panel/pedidos/<int:pk>/estado/",
        PedidoPanelEstadoView.as_view(),
        name="panel-pedidos-estado",
    ),
]
