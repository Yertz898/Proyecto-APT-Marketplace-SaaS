"""El comando que crea las cuentas de demostración de los dos accesos."""

import pytest
from django.core.management import call_command

from apps.tiendas.models import Tienda
from apps.usuarios.models import Rol, Usuario

pytestmark = pytest.mark.django_db

CLAVE = "clave-de-demostracion-97"


@pytest.fixture
def correr(monkeypatch):
    def _correr(clave=CLAVE):
        if clave is None:
            monkeypatch.delenv("DEMO_PASSWORD", raising=False)
        else:
            monkeypatch.setenv("DEMO_PASSWORD", clave)
        call_command("cuentas_demo", verbosity=0)

    return _correr


def test_crea_una_cuenta_por_rol_en_uso(correr):
    correr()

    assert Usuario.objects.count() == 3


def test_separa_los_dos_accesos_por_rol(correr):
    """Los de la plataforma tienen tienda o la administran; el comprador no."""
    correr()

    plataforma = Usuario.objects.exclude(rol=Rol.COMPRADOR)
    assert {u.rol for u in plataforma} == {Rol.ADMIN_PLATAFORMA, Rol.DUENO_TIENDA}
    assert Usuario.objects.get(rol=Rol.COMPRADOR).tienda_id is None


def test_el_dueno_queda_en_la_tienda_de_ejemplo(correr):
    correr()

    assert Usuario.objects.get(rol=Rol.DUENO_TIENDA).tienda == Tienda.objects.get(
        slug="joyas-ye"
    )


def test_la_tienda_de_ejemplo_no_tiene_una_cuenta_de_vendedor(correr):
    """En Joyas Ye el dueño es quien vende: una persona, una cuenta."""
    correr()

    assert not Usuario.objects.filter(rol=Rol.VENDEDOR).exists()


def test_el_administrador_de_plataforma_no_cuelga_de_una_tienda(correr):
    correr()

    admin = Usuario.objects.get(rol=Rol.ADMIN_PLATAFORMA)
    assert admin.tienda_id is None
    assert admin.is_staff and admin.is_superuser


def test_solo_el_administrador_entra_al_admin_de_django(correr):
    correr()

    for cuenta in Usuario.objects.exclude(rol=Rol.ADMIN_PLATAFORMA):
        assert not cuenta.is_staff
        assert not cuenta.is_superuser


def test_las_cuentas_sirven_para_iniciar_sesion(client, correr):
    correr()

    for cuenta in Usuario.objects.all():
        respuesta = client.post(
            "/api/auth/sesion",
            {"email": cuenta.email, "password": CLAVE},
            content_type="application/json",
        )
        assert respuesta.status_code == 200, cuenta.email


def test_correrlo_dos_veces_no_duplica_ni_falla(correr):
    correr()
    correr()

    assert Usuario.objects.count() == 3
    assert Tienda.objects.filter(slug="joyas-ye").count() == 1


def test_la_segunda_corrida_actualiza_la_contrasena(client, correr):
    correr()
    correr(clave="otra-clave-distinta-31")

    respuesta = client.post(
        "/api/auth/sesion",
        {"email": "admin@dealcommerce.cl", "password": "otra-clave-distinta-31"},
        content_type="application/json",
    )
    assert respuesta.status_code == 200


def test_sin_la_variable_de_entorno_genera_una_contrasena(correr, capsys):
    """Una contraseña escrita en el código es una contraseña publicada."""
    correr(clave=None)

    salida = capsys.readouterr().out
    assert "Contraseña generada:" in salida
    assert Usuario.objects.count() == 3


def test_respeta_una_tienda_que_ya_existe(correr):
    Tienda.objects.create(slug="joyas-ye", nombre="Joyas Ye de verdad")

    correr()

    assert Tienda.objects.get(slug="joyas-ye").nombre == "Joyas Ye de verdad"
