"""Rutas de sesión, cuentas y equipo de la tienda."""

from django.urls import path

from apps.usuarios.cuenta import (
    CambiarContrasena,
    ContrasenaDelMiembro,
    EquipoDeLaTienda,
    MiembroDelEquipo,
)
from apps.usuarios.dos_pasos import (
    ConfirmarDosPasos,
    DesactivarDosPasos,
    EstadoDosPasos,
    IniciarDosPasos,
    VerificarAlEntrar,
)
from apps.usuarios.recuperacion import PedirEnlace, Restablecer
from apps.usuarios.views import IniciarSesion, RegistroComprador, RenovarSesion, Yo

urlpatterns = [
    path("auth/sesion", IniciarSesion.as_view(), name="iniciar-sesion"),
    path("auth/sesion/renovar", RenovarSesion.as_view(), name="renovar-sesion"),
    path("auth/sesion/otp", VerificarAlEntrar.as_view(), name="sesion-otp"),
    path("auth/otp", EstadoDosPasos.as_view(), name="otp-estado"),
    path("auth/otp/iniciar", IniciarDosPasos.as_view(), name="otp-iniciar"),
    path("auth/otp/confirmar", ConfirmarDosPasos.as_view(), name="otp-confirmar"),
    path("auth/otp/desactivar", DesactivarDosPasos.as_view(), name="otp-desactivar"),
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
