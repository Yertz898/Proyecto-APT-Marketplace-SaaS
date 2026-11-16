from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auditoria"
    verbose_name = "auditoría"

    def ready(self):
        # Conecta las señales que anotan cada cambio. Se importa acá y no
        # arriba porque los modelos todavía no están cargados al importar apps.
        from apps.auditoria import senales  # noqa: F401
