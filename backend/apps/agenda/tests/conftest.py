"""Fixtures de la agenda. Las de tiendas y usuarios vienen del conftest raíz."""

from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.fixture
def configuracion_a(tienda_a):
    from apps.agenda.models import ConfiguracionAgenda

    return ConfiguracionAgenda.objects.create(
        tienda=tienda_a,
        direccion="Av. Siempre Viva 742, Ñuñoa",
        correo_notificaciones="agenda.a@ejemplo.cl",
    )


@pytest.fixture
def crear_visita(comprador):
    """Crea una visita en un bloque futuro; por omisión, en dos días a las 10:00."""

    def _crear(tienda, *, dias=2, hora=10, posicion=0, duracion=30, **extra):
        from apps.agenda.models import Visita

        inicio = (timezone.now() + timedelta(days=dias)).replace(
            hour=hora, minute=0, second=0, microsecond=0
        )
        datos = {
            "tienda": tienda,
            "comprador": comprador,
            "inicio": inicio,
            "fin": inicio + timedelta(minutes=duracion),
            "posicion": posicion,
            "nombre_contacto": "Compradora",
            "correo_contacto": "compradora@ejemplo.cl",
            "telefono_contacto": "+56 9 1234 5678",
        }
        datos.update(extra)
        return Visita.objects.create(**datos)

    return _crear


@pytest.fixture
def visita_a(tienda_a, crear_visita):
    return crear_visita(tienda_a)


@pytest.fixture
def visita_b(tienda_b, crear_visita):
    return crear_visita(tienda_b)
