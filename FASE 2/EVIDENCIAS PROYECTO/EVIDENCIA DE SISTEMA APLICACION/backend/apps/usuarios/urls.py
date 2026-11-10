"""Rutas de sesión y cuentas."""

from django.urls import path

from apps.usuarios.views import IniciarSesion, RegistroComprador, RenovarSesion, Yo

urlpatterns = [
    path("auth/sesion", IniciarSesion.as_view(), name="iniciar-sesion"),
    path("auth/sesion/renovar", RenovarSesion.as_view(), name="renovar-sesion"),
    path("auth/registro", RegistroComprador.as_view(), name="registro-comprador"),
    path("auth/yo", Yo.as_view(), name="usuario-de-la-sesion"),
]
