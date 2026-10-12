"""
Pruebas del invariante: una tienda nunca ve datos de otra.

Se prueban sobre el manager, que es donde vive el filtro. Cuando existan
endpoints, cada uno suma su prueba de que pedir un recurso de otra tienda
responde 404.
"""

import pytest
from django.contrib.auth.models import AnonymousUser

from apps.clientes.models import AprobacionMayorista

pytestmark = [pytest.mark.django_db, pytest.mark.aislamiento]


def test_el_dueno_solo_ve_las_aprobaciones_de_su_tienda(
    aprobacion_a, aprobacion_b, dueno_a
):
    visibles = AprobacionMayorista.objects.de_usuario(dueno_a)

    assert list(visibles) == [aprobacion_a]
    assert aprobacion_b not in visibles


def test_el_vendedor_solo_ve_las_de_su_tienda(aprobacion_a, aprobacion_b, vendedor_b):
    visibles = AprobacionMayorista.objects.de_usuario(vendedor_b)

    assert list(visibles) == [aprobacion_b]
    assert aprobacion_a not in visibles


def test_el_comprador_no_ve_las_aprobaciones_de_ninguna_tienda(
    aprobacion_a, aprobacion_b, comprador
):
    assert not AprobacionMayorista.objects.de_usuario(comprador).exists()


def test_el_anonimo_no_ve_nada(aprobacion_a, aprobacion_b):
    assert not AprobacionMayorista.objects.de_usuario(AnonymousUser()).exists()


def test_el_administrador_de_plataforma_ve_todas_las_tiendas(
    aprobacion_a, aprobacion_b, admin_plataforma
):
    visibles = AprobacionMayorista.objects.de_usuario(admin_plataforma)

    assert set(visibles) == {aprobacion_a, aprobacion_b}


def test_filtrar_por_tienda_deja_fuera_a_la_otra(aprobacion_a, aprobacion_b, tienda_a):
    visibles = AprobacionMayorista.objects.de_tienda(tienda_a)

    assert list(visibles) == [aprobacion_a]
