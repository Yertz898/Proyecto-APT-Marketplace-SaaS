"""
Crea las cuentas de demostración de los dos accesos del sistema.

Son dos accesos distintos y no se mezclan:

- El de **DealCommerce** (`/panel/entrar`) es para quienes trabajan en la
  plataforma: el administrador, y quienes atienden cada tienda suscrita.

  En Joyas Ye el dueño es también quien vende, así que tiene una sola cuenta.
  El rol `vendedor` existe para una tienda que sí tenga empleados, pero acá no
  se usa y por eso no hay una cuenta de demostración con ese rol.
- El de **cada tienda** (`/t/<slug>/entrar`) es para quien compra en esa
  tienda. Un comprador no pertenece a ninguna tienda.

La contraseña nunca va escrita acá. Se lee de `DEMO_PASSWORD`, y si esa
variable no está definida se genera una al azar y se muestra al terminar. El
repositorio es público: una contraseña en el código es una contraseña
publicada, aunque sea de demostración.

    docker compose exec api python manage.py cuentas_demo

El comando se puede correr las veces que haga falta: si la cuenta ya existe le
actualiza la contraseña y el rol en vez de fallar.
"""

import os
import secrets

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.tiendas.models import Tienda
from apps.usuarios.models import Rol, Usuario

#: Tienda de ejemplo a la que se asocian el dueño y el vendedor.
SLUG_DE_EJEMPLO = "joyas-ye"
NOMBRE_DE_EJEMPLO = "Joyas Ye"

#: Las cuentas, con el acceso por el que entra cada una.
CUENTAS = [
    {
        "email": "admin@dealcommerce.cl",
        "nombre": "Administración DealCommerce",
        "rol": Rol.ADMIN_PLATAFORMA,
        "con_tienda": False,
        "acceso": "DealCommerce",
        "para": "administra las tiendas suscritas",
    },
    {
        "email": "dueno@joyasye.cl",
        "nombre": "Dueño de Joyas Ye",
        "rol": Rol.DUENO_TIENDA,
        "con_tienda": True,
        "acceso": "DealCommerce",
        "para": "administra y vende en su tienda",
    },
    {
        "email": "compradora@ejemplo.cl",
        "nombre": "Compradora de ejemplo",
        "rol": Rol.COMPRADOR,
        "con_tienda": False,
        "acceso": "Tienda",
        "para": "compra en la vitrina de una tienda",
    },
]


def contrasena_a_usar() -> tuple[str, bool]:
    """La de `DEMO_PASSWORD`, o una al azar. Devuelve también si se generó."""
    de_entorno = os.environ.get("DEMO_PASSWORD", "").strip()
    if de_entorno:
        return de_entorno, False
    return secrets.token_urlsafe(12), True


class Command(BaseCommand):
    help = "Crea o actualiza las cuentas de demostración de los dos accesos."

    def handle(self, *args, **opciones):
        contrasena, generada = contrasena_a_usar()

        with transaction.atomic():
            tienda, _ = Tienda.objects.get_or_create(
                slug=SLUG_DE_EJEMPLO, defaults={"nombre": NOMBRE_DE_EJEMPLO}
            )

            for datos in CUENTAS:
                self._crear_o_actualizar(datos, tienda, contrasena)

        self._resumen(contrasena, generada)

    def _crear_o_actualizar(self, datos, tienda, contrasena):
        cuenta = Usuario.objects.filter(email=datos["email"]).first()

        if cuenta is None:
            cuenta = Usuario(email=datos["email"])
            verbo = "creada"
        else:
            verbo = "actualizada"

        cuenta.nombre = datos["nombre"]
        cuenta.rol = datos["rol"]
        cuenta.tienda = tienda if datos["con_tienda"] else None
        cuenta.is_active = True
        # El administrador de plataforma entra al admin de Django; el resto no.
        cuenta.is_staff = datos["rol"] == Rol.ADMIN_PLATAFORMA
        cuenta.is_superuser = datos["rol"] == Rol.ADMIN_PLATAFORMA
        cuenta.set_password(contrasena)
        cuenta.full_clean()
        cuenta.save()

        self.stdout.write(f"  {verbo}: {datos['email']} ({cuenta.get_rol_display()})")

    def _resumen(self, contrasena, generada):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Acceso DealCommerce — /panel/entrar"))
        for datos in CUENTAS:
            if datos["acceso"] == "DealCommerce":
                self.stdout.write(f"  {datos['email']:<28} {datos['para']}")

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Acceso de la tienda — /t/{SLUG_DE_EJEMPLO}/entrar")
        )
        for datos in CUENTAS:
            if datos["acceso"] == "Tienda":
                self.stdout.write(f"  {datos['email']:<28} {datos['para']}")

        self.stdout.write("")
        if generada:
            self.stdout.write(f"Contraseña generada: {contrasena}")
            self.stdout.write(
                "Anótala: no queda guardada en ninguna parte. Para fijar una "
                "propia, define DEMO_PASSWORD en el .env."
            )
        else:
            self.stdout.write("Contraseña: la de DEMO_PASSWORD.")

        self.stdout.write(
            self.style.WARNING(
                "Son cuentas de demostración. No deben existir en producción."
            )
        )
