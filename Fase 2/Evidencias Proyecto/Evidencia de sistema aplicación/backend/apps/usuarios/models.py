"""
Cuentas, roles y pertenencia a una tienda.

El rol determina qué puede hacer una persona; la tienda a la que pertenece
determina qué datos puede ver. Los cuatro roles son los del CLAUDE.md y no hay
más.
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from apps.usuarios.validadores import normalizar_rut, validar_rut


class Rol(models.TextChoices):
    ADMIN_PLATAFORMA = "admin_plataforma", "Administrador de plataforma"
    DUENO_TIENDA = "dueno_tienda", "Dueño de tienda"
    VENDEDOR = "vendedor", "Vendedor"
    COMPRADOR = "comprador", "Comprador"


#: Roles que trabajan dentro de una tienda y por lo tanto deben tener una.
ROLES_DE_TIENDA = (Rol.DUENO_TIENDA, Rol.VENDEDOR)

#: Roles que no pertenecen a ninguna tienda.
ROLES_SIN_TIENDA = (Rol.ADMIN_PLATAFORMA, Rol.COMPRADOR)


class GestorDeUsuarios(BaseUserManager):
    """La cuenta se identifica por correo, no por nombre de usuario."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("El correo es obligatorio.")

        email = self.normalize_email(email).lower()
        usuario = self.model(email=email, **extra)
        usuario.set_password(password)
        usuario.full_clean()
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("rol", Rol.ADMIN_PLATAFORMA)
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)

        if extra["is_staff"] is not True or extra["is_superuser"] is not True:
            raise ValueError(
                "Un superusuario necesita is_staff e is_superuser en True."
            )

        return self.create_user(email, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("correo", unique=True)
    nombre = models.CharField("nombre", max_length=150)

    # El RUT es dato del comprador, no credencial: sirve para boletas y despachos.
    # Puede quedar vacío; si viene, se guarda normalizado y validado.
    rut = models.CharField(
        "RUT",
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        validators=[validar_rut],
        help_text="Formato 12345678-5, sin puntos.",
    )

    rol = models.CharField("rol", max_length=20, choices=Rol.choices)

    # Nula para el administrador de plataforma y para el comprador: ninguno de
    # los dos pertenece a una tienda.
    tienda = models.ForeignKey(
        "tiendas.Tienda",
        verbose_name="tienda",
        on_delete=models.PROTECT,
        related_name="usuarios",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField("activo", default=True)
    is_staff = models.BooleanField("puede entrar al panel de Django", default=False)
    fecha_registro = models.DateTimeField("fecha de registro", auto_now_add=True)

    objects = GestorDeUsuarios()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre", "rol"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = [
            # El invariante del sistema empieza acá: un vendedor sin tienda no
            # se puede acotar a ninguna, y un comprador con tienda confundiría
            # a quién pertenece.
            models.CheckConstraint(
                condition=(
                    models.Q(rol__in=ROLES_DE_TIENDA, tienda__isnull=False)
                    | models.Q(rol__in=ROLES_SIN_TIENDA, tienda__isnull=True)
                ),
                name="usuario_tienda_segun_rol",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} <{self.email}>"

    def clean(self):
        super().clean()
        self.email = self.email.lower()
        if self.rut:
            self.rut = normalizar_rut(self.rut)

    @property
    def es_admin_plataforma(self) -> bool:
        return self.rol == Rol.ADMIN_PLATAFORMA

    @property
    def trabaja_en_tienda(self) -> bool:
        """Dueño o vendedor: ve y administra los datos de su tienda."""
        return self.rol in ROLES_DE_TIENDA
