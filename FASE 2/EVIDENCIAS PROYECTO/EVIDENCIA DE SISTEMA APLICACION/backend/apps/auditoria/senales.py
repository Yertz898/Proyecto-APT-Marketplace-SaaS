"""
Cada alta, cambio y baja hecha desde la API queda anotada sola.

Se hace con señales y no vista por vista porque así una vista nueva queda
registrada sin que nadie tenga que acordarse. Solo se anota lo que ocurre dentro
de una petición: las cargas por comando (los datos de demostración, las
migraciones) no son acciones de una persona y llenarían el registro de ruido.

Las operaciones masivas (`bulk_create`, `update`) no disparan señales. Las
cargas masivas quedan registradas igual, por la carga que se confirmó.
"""

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.auditoria.contexto import peticion_en_curso
from apps.auditoria.models import Accion
from apps.auditoria.registrar import registrar

# Las apps cuyos datos se registran, y los modelos que se dejan fuera porque
# solo repiten lo que ya dice su padre (las líneas de un pedido) o son
# mecánica interna (los correos en cola).
APPS_REGISTRADAS = {
    "catalogo",
    "precios",
    "pedidos",
    "agenda",
    "tiendas",
    "usuarios",
    "ingesta",
    "clientes",
}
MODELOS_EXCLUIDOS = {"LineaPedido", "EnvioCorreo"}

# Campos que nunca se copian al detalle: secretos, o ruido que cambia solo.
CAMPOS_OMITIDOS = {
    "password",
    "last_login",
    "fecha_edicion",
    "token_feed",
    "secuencia",
}


def _se_registra(sender) -> bool:
    return (
        sender._meta.app_label in APPS_REGISTRADAS
        and sender.__name__ not in MODELOS_EXCLUIDOS
    )


def _tienda_de(instancia):
    from apps.tiendas.models import Tienda

    if isinstance(instancia, Tienda):
        return instancia
    tienda_id = getattr(instancia, "tienda_id", None)
    if not tienda_id:
        return None
    return Tienda.objects.filter(pk=tienda_id).first()


def _simple(valor):
    if hasattr(valor, "name") and not isinstance(valor, str):
        return valor.name or ""  # archivos: basta con el nombre
    if isinstance(valor, (int, float, bool, str, type(None))):
        return valor
    return str(valor)


def _valores(instancia) -> dict:
    return {
        campo.name: _simple(getattr(instancia, campo.attname))
        for campo in instancia._meta.concrete_fields
        if campo.name not in CAMPOS_OMITIDOS
    }


@receiver(pre_save)
def _recordar_lo_anterior(sender, instance, **kwargs):
    if peticion_en_curso() is None or not _se_registra(sender) or not instance.pk:
        return
    anterior = sender._default_manager.filter(pk=instance.pk).first()
    instance._valores_anteriores = _valores(anterior) if anterior else None


@receiver(post_save)
def _anotar_guardado(sender, instance, created, **kwargs):
    if peticion_en_curso() is None or not _se_registra(sender):
        return

    if created:
        accion, detalle = Accion.CREAR, {}
    else:
        anteriores = getattr(instance, "_valores_anteriores", None) or {}
        detalle = {
            campo: {"antes": anteriores.get(campo), "despues": valor}
            for campo, valor in _valores(instance).items()
            if anteriores.get(campo) != valor
        }
        if not detalle:
            return  # se guardó sin cambiar nada
        accion = Accion.MODIFICAR

    registrar(
        accion,
        sender._meta.verbose_name,
        instance,
        tienda=_tienda_de(instance),
        detalle=detalle,
    )


@receiver(post_delete)
def _anotar_borrado(sender, instance, **kwargs):
    if peticion_en_curso() is None or not _se_registra(sender):
        return
    registrar(
        Accion.ELIMINAR,
        sender._meta.verbose_name,
        instance,
        tienda=_tienda_de(instance),
    )
