"""Rutas de pagos: el retorno desde Webpay."""

from django.urls import path

from apps.pagos.views import Retorno

urlpatterns = [
    path("pagos/webpay/retorno", Retorno.as_view(), name="webpay-retorno"),
]
