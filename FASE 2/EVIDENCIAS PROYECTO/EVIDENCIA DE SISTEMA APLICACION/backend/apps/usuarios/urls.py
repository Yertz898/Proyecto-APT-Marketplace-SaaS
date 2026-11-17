"""Rutas de sesión, cuentas y equipo de la tienda."""

from django.urls import path

from apps.usuarios.cuenta import (
    CambiarContrasena,
    ContrasenaDelMiembro,
    EquipoDeLaTienda,
    MiembroDelEquipo,
)
from apps.usuarios.recuperacion import PedirEnlace, Restablecer
from apps.usuarios.views import IniciarSesion, RegistroComprador, RenovarSesion, Yo

urlpatterns = [
    path("auth/sesion", IniciarSesion.as_view(), name="iniciar-sesion"),
    path("auth/sesion/renovar", RenovarSesion.as_view(), name="renovar-sesion"),
    path("auth/registro", RegistroComprador.as_view(), name="registro-comprador"),
    path("auth/yo", Yo.as_view(), name="usuario-de-la-sesion"),
    path("auth/contrasena", CambiarContrasena.as_view(), name="cambiar-contrasena"),
    path("auth/contrasena/olvido", PedirEnlace.as_view(), name="olvido-contrasena"),
    path(
        "auth/contrasena/restablecer",
        Restablecer.as_view(),
        name="restablecer-contrasena",
    ),
    path("panel/equipo", EquipoDeLaTienda.as_view(), name="panel-equipo"),
    path("panel/equipo/<int:pk>", MiembroDelEquipo.as_view(), name="panel-miembro"),
    path(
        "panel/equipo/<int:pk>/contrasena",
        ContrasenaDelMiembro.as_view(),
        name="panel-miembro-contrasena",
    ),
]
