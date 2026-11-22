"""
Manda los avisos de la agenda que quedaron pendientes o fallaron.

Los avisos se registran siempre en EnvioCorreo, pero solo salen con
CORREOS_AGENDA_ACTIVOS encendido (ver `apps/agenda/avisos.py`). El día que se
encienda, esto manda lo acumulado:

    docker compose exec api python manage.py enviar_correos_agenda

Con --desde-dias se limita a los avisos recientes: un aviso de un cambio de
hora de hace un mes ya no le sirve a nadie.
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.agenda.avisos import enviar
from apps.agenda.models import EnvioCorreo, EstadoEnvio

#: Después de tantos intentos fallidos, un aviso se deja de reintentar.
MAXIMO_DE_INTENTOS = 5


class Command(BaseCommand):
    help = "Envía los avisos de la agenda pendientes o fallidos."

    def add_arguments(self, parser):
        parser.add_argument("--desde-dias", type=int, default=7)
        parser.add_argument(
            "--aunque-este-apagado",
            action="store_true",
            help="Envía aunque CORREOS_AGENDA_ACTIVOS esté en False.",
        )

    def handle(self, *args, desde_dias, aunque_este_apagado, **opciones):
        if not settings.CORREOS_AGENDA_ACTIVOS and not aunque_este_apagado:
            raise CommandError(
                "Los correos de la agenda están apagados "
                "(CORREOS_AGENDA_ACTIVOS=False)."
            )

        desde = timezone.now() - timedelta(days=desde_dias)
        pendientes = list(
            EnvioCorreo.objects.filter(
                estado__in=[EstadoEnvio.PENDIENTE, EstadoEnvio.FALLIDO],
                intentos__lt=MAXIMO_DE_INTENTOS,
                fecha_creacion__gte=desde,
            ).order_by("fecha_creacion")
        )

        enviados = sum(1 for envio in pendientes if enviar(envio))
        self.stdout.write(
            f"Enviados {enviados} de {len(pendientes)} avisos pendientes."
        )
