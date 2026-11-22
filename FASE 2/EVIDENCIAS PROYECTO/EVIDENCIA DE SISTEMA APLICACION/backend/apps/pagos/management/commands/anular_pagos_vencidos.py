"""
Anula los pedidos cuyo pago con Webpay nunca volvió (hace más de 15 minutos).

Un cliente que abre Webpay y cierra la pestaña deja su pedido pendiente y el
stock reservado. Esto lo suelta. También se hace solo al iniciar un pago nuevo
en la misma tienda; el comando sirve para correrlo con un cron.

    docker compose exec api python manage.py anular_pagos_vencidos
"""

from django.core.management.base import BaseCommand

from apps.pagos.servicios import anular_vencidos


class Command(BaseCommand):
    help = "Anula los pedidos con pagos de Webpay que no volvieron."

    def handle(self, *args, **opciones):
        cuantos = anular_vencidos()
        self.stdout.write(f"Pagos vencidos anulados: {cuantos}.")
