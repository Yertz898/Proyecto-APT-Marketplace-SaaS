"""Pruebas del modelo Usuario: identificación por correo, RUT y roles."""

import pytest
from django.core.exceptions import ValidationError

from apps.usuarios.models import Rol, Usuario
from apps.usuarios.validadores import digito_verificador, normalizar_rut

pytestmark = pytest.mark.django_db


def crear(**extra):
    datos = {
        "email": "persona@ejemplo.cl",
        "password": "clave-de-prueba",
        "nombre": "Persona",
        "rol": Rol.COMPRADOR,
    }
    datos.update(extra)
    return Usuario.objects.create_user(**datos)


def test_el_correo_se_guarda_en_minusculas():
    usuario = crear(email="Persona@Ejemplo.CL")

    assert usuario.email == "persona@ejemplo.cl"


def test_el_correo_es_obligatorio():
    with pytest.raises(ValueError):
        crear(email="")


def test_el_rut_se_guarda_normalizado():
    usuario = crear(rut="12.345.678-5")

    assert usuario.rut == "12345678-5"


def test_un_rut_con_digito_verificador_equivocado_se_rechaza():
    with pytest.raises(ValidationError) as error:
        crear(rut="12345678-9")

    assert "rut" in error.value.message_dict


def test_un_rut_sin_formato_se_rechaza():
    with pytest.raises(ValidationError):
        crear(rut="12345678")


def test_el_rut_puede_quedar_vacio():
    assert crear().rut is None


@pytest.mark.parametrize(
    ("cuerpo", "esperado"),
    [("12345678", "5"), ("11111111", "1"), ("6", "K"), ("14", "0"), ("19", "1")],
)
def test_digito_verificador(cuerpo, esperado):
    assert digito_verificador(cuerpo) == esperado


def test_normalizar_rut_saca_puntos_y_sube_la_k():
    assert normalizar_rut(" 7.654.321-k ") == "7654321-K"


def test_un_vendedor_necesita_tienda():
    with pytest.raises(ValidationError):
        crear(email="vendedor@ejemplo.cl", rol=Rol.VENDEDOR)


def test_un_comprador_no_puede_pertenecer_a_una_tienda(tienda_a):
    with pytest.raises(ValidationError):
        crear(email="otro@ejemplo.cl", rol=Rol.COMPRADOR, tienda=tienda_a)


def test_el_dueno_trabaja_en_su_tienda(dueno_a, tienda_a):
    assert dueno_a.trabaja_en_tienda
    assert not dueno_a.es_admin_plataforma
    assert dueno_a.tienda == tienda_a


def test_el_administrador_de_plataforma_no_tiene_tienda(admin_plataforma):
    assert admin_plataforma.es_admin_plataforma
    assert admin_plataforma.tienda is None
