"""
Los avisos por correo de la agenda: listos, pero apagados.

Cada aviso se **registra** siempre en `EnvioCorreo`, con su asunto y su texto
ya armados. Solo **sale** si `settings.CORREOS_AGENDA_ACTIVOS` está encendido.
Mientras no haya un dominio verificado en Resend, Resend solo entrega a la
dueña de la cuenta, así que el proyecto lo deja apagado y la información le
llega a cada parte dentro del sistema: el dueño en su panel y el cliente en
«Mis citas».

El día que se verifique el dominio basta con encender la variable. Los avisos
que quedaron pendientes se mandan con `manage.py enviar_correos_agenda`.

Un aviso nunca hace fallar lo que lo provocó: si el correo falla, el cambio de
hora ya quedó hecho y el fallo queda anotado en el registro para reintentarlo.
"""

import logging

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils import timezone

from apps.agenda.models import (
    CambioDeHora,
    ConfiguracionAgenda,
    EnvioCorreo,
    EstadoEnvio,
    LadoDelCambio,
    TipoCorreo,
    Visita,
)
from apps.core.correo import enviar_correo

registro = logging.getLogger(__name__)

#: Con qué se firman los enlaces de Aceptar / Rechazar del correo.
SAL_DEL_ENLACE = "agenda.cambio-de-hora"
#: Cuánto vale un enlace: una semana, más que la ventana típica de una agenda.
VIGENCIA_DEL_ENLACE = 7 * 24 * 60 * 60


def firmar_cambio(cambio: CambioDeHora) -> str:
    """La firma que va en el enlace del correo: qué cambio y quién responde."""
    return signing.TimestampSigner(salt=SAL_DEL_ENLACE).sign_object(
        {"cambio": cambio.pk, "lado": cambio.responde}
    )


def leer_firma(firma: str) -> dict:
    """Lo firmado, o `signing.BadSignature` si es falso o venció."""
    return signing.TimestampSigner(salt=SAL_DEL_ENLACE).unsign_object(
        firma, max_age=VIGENCIA_DEL_ENLACE
    )


# ── A quién y cuándo ────────────────────────────────────────────────────────


def _correo_de_la_tienda(visita: Visita) -> str | None:
    """El correo de notificaciones de la agenda o, si no hay, el del dueño."""
    configuracion = ConfiguracionAgenda.objects.filter(
        tienda_id=visita.tienda_id
    ).first()
    if configuracion and configuracion.correo_notificaciones:
        return configuracion.correo_notificaciones

    from apps.usuarios.models import Rol, Usuario

    dueno = Usuario.objects.filter(
        tienda_id=visita.tienda_id, rol=Rol.DUENO_TIENDA, is_active=True
    ).first()
    return dueno.email if dueno else None


def _cuando(momento) -> str:
    local = timezone.localtime(momento)
    return local.strftime("%d-%m-%Y a las %H:%M")


def _enlace_del_cliente(visita: Visita) -> str:
    return f"{settings.FRONTEND_URL}/t/{visita.tienda.slug}/cuenta/citas"


def _enlace_de_la_tienda() -> str:
    return f"{settings.FRONTEND_URL}/panel/agenda"


def _registrar(
    visita: Visita, tipo: str, destinatario: str | None, asunto: str, cuerpo: str
):
    if not destinatario:
        return None
    envio = EnvioCorreo.objects.create(
        tienda_id=visita.tienda_id,
        visita=visita,
        tipo=tipo,
        destinatario=destinatario,
        asunto=asunto[:200],
        cuerpo=cuerpo,
    )
    if settings.CORREOS_AGENDA_ACTIVOS:
        # Después del commit: si lo que provocó el aviso se deshace, el
        # correo no sale.
        transaction.on_commit(lambda: enviar(envio))
    return envio


def enviar(envio: EnvioCorreo) -> bool:
    """Manda un aviso registrado y anota cómo le fue. No lanza excepciones."""
    envio.intentos += 1
    try:
        enviar_correo(envio.destinatario, envio.asunto, envio.cuerpo)
    except Exception as error:  # noqa: BLE001
        envio.estado = EstadoEnvio.FALLIDO
        envio.ultimo_error = str(error)[:500]
        envio.save(update_fields=["intentos", "estado", "ultimo_error"])
        registro.warning("No salió el aviso %s: %s", envio.pk, type(error).__name__)
        return False
    envio.estado = EstadoEnvio.ENVIADO
    envio.enviado_en = timezone.now()
    envio.ultimo_error = ""
    envio.save(update_fields=["intentos", "estado", "ultimo_error", "enviado_en"])
    return True


# ── Los avisos ──────────────────────────────────────────────────────────────


def cambio_propuesto(cambio: CambioDeHora) -> None:
    """Le avisa a quien tiene que responder, con enlaces para hacerlo."""
    visita = cambio.visita
    tienda = visita.tienda.nombre
    firma = firmar_cambio(cambio)
    aceptar = f"{settings.FRONTEND_URL}/agenda/cambio?firma={firma}&respuesta=aceptar"
    rechazar = f"{settings.FRONTEND_URL}/agenda/cambio?firma={firma}&respuesta=rechazar"

    if cambio.responde == LadoDelCambio.TIENDA:
        destinatario = _correo_de_la_tienda(visita)
        asunto = f"{visita.nombre_contacto} pide cambiar su visita"
        saludo = f"{visita.nombre_contacto} pide mover su visita a {tienda}."
        panel = _enlace_de_la_tienda()
    else:
        destinatario = visita.correo_contacto
        asunto = f"{tienda} te propone otra hora para tu visita"
        saludo = f"Hola {visita.nombre_contacto}: {tienda} te propone otra hora."
        panel = _enlace_del_cliente(visita)

    cuerpo = (
        f"{saludo}\n\n"
        f"Hora actual: {_cuando(visita.inicio)}\n"
        f"Hora propuesta: {_cuando(cambio.inicio)}\n\n"
        f"Aceptar el cambio: {aceptar}\n"
        f"Rechazarlo (la visita se cancela): {rechazar}\n\n"
        f"También puedes responder desde {panel}\n"
    )
    _registrar(visita, TipoCorreo.CAMBIO_PROPUESTO, destinatario, asunto, cuerpo)


def cambio_aceptado(cambio: CambioDeHora) -> None:
    """A las dos partes: la visita quedó a la hora nueva."""
    visita = cambio.visita
    tienda = visita.tienda.nombre
    texto = (
        f"La visita de {visita.nombre_contacto} a {tienda} se movió.\n\n"
        f"Nueva hora: {_cuando(visita.inicio)}\n"
    )
    asunto = f"Visita reprogramada: {_cuando(visita.inicio)}"
    _registrar(
        visita,
        TipoCorreo.REPROGRAMADA,
        visita.correo_contacto,
        asunto,
        texto + f"\nTus citas: {_enlace_del_cliente(visita)}\n",
    )
    _registrar(
        visita,
        TipoCorreo.REPROGRAMADA,
        _correo_de_la_tienda(visita),
        asunto,
        texto + f"\nTu agenda: {_enlace_de_la_tienda()}\n",
    )


def visita_cancelada(visita: Visita, *, por: str, motivo: str = "") -> None:
    """
    Avisa que la visita se canceló, a la parte que no la canceló.

    `por` es el lado que provocó la cancelación: si fue la tienda (o el cliente
    rechazó su propuesta de cambio), se le avisa al cliente, y al revés.
    """
    tienda = visita.tienda.nombre
    detalle = f"\nMotivo: {motivo}\n" if motivo else ""
    if por == LadoDelCambio.TIENDA:
        _registrar(
            visita,
            TipoCorreo.CANCELADA,
            visita.correo_contacto,
            f"Tu visita a {tienda} se canceló",
            f"Hola {visita.nombre_contacto}: tu visita a {tienda} del "
            f"{_cuando(visita.inicio)} quedó cancelada.\n{detalle}\n"
            "Puedes pedir otra hora en "
            f"{settings.FRONTEND_URL}/t/{visita.tienda.slug}/agenda\n",
        )
    else:
        _registrar(
            visita,
            TipoCorreo.CANCELADA,
            _correo_de_la_tienda(visita),
            f"{visita.nombre_contacto} canceló su visita",
            f"La visita de {visita.nombre_contacto} del {_cuando(visita.inicio)} "
            f"quedó cancelada.\n{detalle}\nTu agenda: {_enlace_de_la_tienda()}\n",
        )
