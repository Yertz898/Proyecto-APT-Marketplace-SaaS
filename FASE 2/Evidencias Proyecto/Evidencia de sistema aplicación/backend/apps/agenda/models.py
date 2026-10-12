"""
Agenda de visitas a la oficina de la tienda.

Cada tienda configura sus propios horarios, dirección y reglas: nada de esto se
escribe en el código. Las visitas cuelgan de la tienda, así que el aislamiento
lo da la capa común de apps.core.
"""

import secrets
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import ModeloDeTienda

#: Largo del token del feed de calendario. Tiene que ser largo y aleatorio
#: porque esa URL no pide sesión y expone datos de compradores.
LARGO_TOKEN_FEED = 32


def generar_token_feed() -> str:
    return secrets.token_urlsafe(LARGO_TOKEN_FEED)


class DiaSemana(models.IntegerChoices):
    LUNES = 0, "Lunes"
    MARTES = 1, "Martes"
    MIERCOLES = 2, "Miércoles"
    JUEVES = 3, "Jueves"
    VIERNES = 4, "Viernes"
    SABADO = 5, "Sábado"
    DOMINGO = 6, "Domingo"


class ConfiguracionAgenda(ModeloDeTienda):
    """Reglas de la agenda de una tienda. Una sola por tienda."""

    duracion_minutos = models.PositiveSmallIntegerField(
        "duración de cada visita en minutos",
        default=30,
        help_text="Con esto se calculan los bloques disponibles.",
    )

    visitas_por_bloque = models.PositiveSmallIntegerField(
        "visitas simultáneas por bloque",
        default=1,
    )

    anticipacion_minima_horas = models.PositiveSmallIntegerField(
        "anticipación mínima en horas",
        default=24,
        help_text="No se puede pedir hora con menos anticipación que esta.",
    )

    ventana_maxima_dias = models.PositiveSmallIntegerField(
        "ventana máxima en días",
        default=30,
        help_text="Hasta cuántos días hacia adelante se puede reservar.",
    )

    confirmacion_automatica = models.BooleanField(
        "confirmación automática",
        default=False,
        help_text="Apagada, cada solicitud espera a que el dueño la acepte.",
    )

    direccion = models.CharField("dirección de la oficina", max_length=250, blank=True)
    indicaciones = models.TextField("cómo llegar", blank=True)

    correo_notificaciones = models.EmailField("correo de notificaciones", blank=True)

    # URL privada del feed de calendario del dueño. Se puede regenerar, y al
    # hacerlo la anterior deja de servir.
    token_feed = models.CharField(
        "token del feed de calendario",
        max_length=64,
        unique=True,
        default=generar_token_feed,
    )

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "configuración de agenda"
        verbose_name_plural = "configuraciones de agenda"
        constraints = [
            models.UniqueConstraint(
                fields=["tienda"], name="agenda_una_configuracion_por_tienda"
            ),
            models.CheckConstraint(
                condition=models.Q(duracion_minutos__gt=0),
                name="agenda_duracion_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(visitas_por_bloque__gt=0),
                name="agenda_capacidad_positiva",
            ),
        ]

    def __str__(self):
        return f"Agenda de {self.tienda}"

    def regenerar_token_feed(self) -> str:
        """Invalida la URL anterior del feed. El dueño debe volver a suscribirla."""
        self.token_feed = generar_token_feed()
        self.save(update_fields=["token_feed", "fecha_edicion"])
        return self.token_feed


class BloqueHorario(ModeloDeTienda):
    """
    Un tramo de atención, semanal o de una fecha puntual.

    Varias filas del mismo día son lo que permite el horario partido: 10:00 a
    13:00 y 15:00 a 18:00 son dos bloques del lunes.

    Cada bloque puede definir su propia duración, capacidad, nombre y forma de
    confirmación. Lo que deja en blanco lo hereda de la configuración de la
    tienda, así que crear un bloque simple sigue siendo elegir día y horario.
    """

    nombre = models.CharField(
        "nombre del bloque",
        max_length=80,
        blank=True,
        help_text="Visible para el comprador, por ejemplo «Atención mayoristas».",
    )

    # Un bloque es semanal o de una fecha puntual, nunca las dos cosas.
    dia_semana = models.IntegerField(
        "día de la semana", choices=DiaSemana.choices, blank=True, null=True
    )
    fecha = models.DateField("fecha puntual", blank=True, null=True)

    hora_inicio = models.TimeField("hora de inicio")
    hora_fin = models.TimeField("hora de término")

    # Los tres campos siguientes, en blanco, significan «lo que diga la tienda».
    duracion_minutos = models.PositiveSmallIntegerField(
        "duración de cada visita en minutos", blank=True, null=True
    )
    visitas_simultaneas = models.PositiveSmallIntegerField(
        "visitas simultáneas", blank=True, null=True
    )
    confirmacion_automatica = models.BooleanField(
        "confirmación automática", blank=True, null=True
    )

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "bloque de atención"
        verbose_name_plural = "bloques de atención"
        ordering = ["fecha", "dia_semana", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["tienda", "dia_semana", "hora_inicio"],
                condition=models.Q(dia_semana__isnull=False),
                name="agenda_bloque_semanal_unico",
            ),
            models.UniqueConstraint(
                fields=["tienda", "fecha", "hora_inicio"],
                condition=models.Q(fecha__isnull=False),
                name="agenda_bloque_puntual_unico",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(dia_semana__isnull=False, fecha__isnull=True)
                    | models.Q(dia_semana__isnull=True, fecha__isnull=False)
                ),
                name="agenda_bloque_semanal_o_puntual",
            ),
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F("hora_inicio")),
                name="agenda_bloque_termina_despues_de_empezar",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(duracion_minutos__isnull=True)
                    | models.Q(duracion_minutos__gt=0)
                ),
                name="agenda_bloque_duracion_positiva",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(visitas_simultaneas__isnull=True)
                    | models.Q(visitas_simultaneas__gt=0)
                ),
                name="agenda_bloque_capacidad_positiva",
            ),
        ]

    def __str__(self):
        cuando = (
            f"{self.fecha:%d-%m-%Y}"
            if self.es_puntual
            else self.get_dia_semana_display()
        )
        etiqueta = f"{self.nombre}: " if self.nombre else ""
        return f"{etiqueta}{cuando} {self.hora_inicio:%H:%M}–{self.hora_fin:%H:%M}"

    @property
    def es_puntual(self) -> bool:
        return self.fecha is not None

    def aplica_en(self, fecha) -> bool:
        """Si este bloque abre atención en esa fecha."""
        if self.es_puntual:
            return self.fecha == fecha
        return self.dia_semana == fecha.weekday()

    # ── Valores efectivos: lo propio si está definido; si no, lo de la tienda ──

    def duracion(self, configuracion) -> int:
        return self.duracion_minutos or configuracion.duracion_minutos

    def capacidad(self, configuracion) -> int:
        return self.visitas_simultaneas or configuracion.visitas_por_bloque

    def confirma_solo(self, configuracion) -> bool:
        if self.confirmacion_automatica is None:
            return configuracion.confirmacion_automatica
        return self.confirmacion_automatica

    def clean(self):
        super().clean()
        self.validar_sin_solapes()

    def validar_sin_solapes(self):
        """
        Dos bloques del mismo día no pueden pisarse: las horas disponibles
        saldrían duplicadas y el comprador vería el mismo cupo dos veces.
        """
        if not self.tienda_id or self.hora_inicio is None or self.hora_fin is None:
            return
        if self.dia_semana is None and self.fecha is None:
            return

        hermanos = BloqueHorario.objects.de_tienda(self.tienda_id).exclude(pk=self.pk)
        if self.es_puntual:
            hermanos = hermanos.filter(fecha=self.fecha)
        else:
            hermanos = hermanos.filter(dia_semana=self.dia_semana)

        solapado = hermanos.filter(
            hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio
        ).first()

        if solapado:
            raise ValidationError(
                {"hora_inicio": f"Este horario se cruza con «{solapado}»."},
                code="bloques_solapados",
            )


class DiaBloqueado(ModeloDeTienda):
    """Feriados, vacaciones o días puntuales sin atención."""

    fecha = models.DateField("fecha")
    motivo = models.CharField("motivo", max_length=150, blank=True)

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "día bloqueado"
        verbose_name_plural = "días bloqueados"
        ordering = ["fecha"]
        constraints = [
            models.UniqueConstraint(
                fields=["tienda", "fecha"], name="agenda_dia_bloqueado_unico"
            ),
        ]

    def __str__(self):
        return f"{self.fecha:%d-%m-%Y} {self.motivo}".strip()


class EstadoVisita(models.TextChoices):
    SOLICITADA = "solicitada", "Solicitada"
    CONFIRMADA = "confirmada", "Confirmada"
    ASISTIDA = "asistida", "Asistida"
    NO_ASISTIO = "no_asistio", "No asistió"
    RECHAZADA = "rechazada", "Rechazada"
    CANCELADA = "cancelada", "Cancelada"


#: Transiciones válidas, en un solo lugar. Una transición que no esté acá es un
#: error de validación, no un `assert`.
TRANSICIONES: dict[str, set[str]] = {
    EstadoVisita.SOLICITADA: {
        EstadoVisita.CONFIRMADA,
        EstadoVisita.RECHAZADA,
        EstadoVisita.CANCELADA,
    },
    EstadoVisita.CONFIRMADA: {
        EstadoVisita.ASISTIDA,
        EstadoVisita.NO_ASISTIO,
        EstadoVisita.CANCELADA,
    },
    EstadoVisita.ASISTIDA: set(),
    EstadoVisita.NO_ASISTIO: set(),
    EstadoVisita.RECHAZADA: set(),
    EstadoVisita.CANCELADA: set(),
}

#: Estados que mantienen ocupado el asiento del bloque. Una visita rechazada o
#: cancelada libera su cupo.
ESTADOS_QUE_OCUPAN = (
    EstadoVisita.SOLICITADA,
    EstadoVisita.CONFIRMADA,
    EstadoVisita.ASISTIDA,
    EstadoVisita.NO_ASISTIO,
)


class Visita(ModeloDeTienda):
    """
    Una visita a la oficina de la tienda.

    El horario se guarda en UTC y se muestra en hora de Chile. Chile cambia de
    horario en abril y septiembre: guardar en local dejaría visitas corridas una
    hora después del cambio.
    """

    # Identificador estable del evento de calendario. Es lo que hace que una
    # reprogramación reemplace el evento en vez de duplicarlo.
    uid = models.UUIDField(
        "identificador de calendario", default=uuid.uuid4, editable=False, unique=True
    )

    comprador = models.ForeignKey(
        "usuarios.Usuario",
        verbose_name="comprador",
        on_delete=models.PROTECT,
        related_name="visitas",
    )

    inicio = models.DateTimeField("inicio")
    fin = models.DateTimeField("término")

    # Asiento numerado dentro del bloque. Es lo que impide pasarse de capacidad
    # aunque falle la verificación previa: dos reservas no pueden tomar el mismo
    # asiento del mismo bloque.
    posicion = models.PositiveSmallIntegerField("asiento en el bloque", default=0)

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=EstadoVisita.choices,
        default=EstadoVisita.SOLICITADA,
    )

    nombre_contacto = models.CharField("nombre de contacto", max_length=150)
    correo_contacto = models.EmailField("correo de contacto")
    telefono_contacto = models.CharField("teléfono de contacto", max_length=30)
    motivo = models.TextField("motivo de la visita", blank=True)

    motivo_rechazo = models.TextField("motivo del rechazo", blank=True)

    # Aumenta en cada cambio que el calendario tiene que conocer. Va como
    # SEQUENCE en el archivo .ics.
    secuencia = models.PositiveIntegerField("secuencia del evento", default=0)

    recordatorio_enviado_en = models.DateTimeField(
        "recordatorio enviado en", blank=True, null=True
    )

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "visita"
        verbose_name_plural = "visitas"
        ordering = ["-inicio"]
        constraints = [
            # La capacidad del bloque la garantiza la base de datos: cada visita
            # toma un asiento numerado y no puede haber dos iguales en el mismo
            # bloque mientras la visita ocupe cupo.
            models.UniqueConstraint(
                fields=["tienda", "inicio", "posicion"],
                condition=models.Q(estado__in=ESTADOS_QUE_OCUPAN),
                name="agenda_asiento_unico_por_bloque",
            ),
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("inicio")),
                name="agenda_visita_termina_despues_de_empezar",
            ),
        ]
        indexes = [
            models.Index(fields=["tienda", "inicio"]),
            models.Index(fields=["tienda", "estado"]),
        ]

    def __str__(self):
        return f"{self.nombre_contacto} el {self.inicio:%d-%m-%Y %H:%M}"

    @property
    def ocupa_cupo(self) -> bool:
        return self.estado in ESTADOS_QUE_OCUPAN

    def puede_pasar_a(self, estado: str) -> bool:
        return estado in TRANSICIONES[self.estado]

    def cambiar_estado(self, estado: str, *, motivo_rechazo: str = "") -> None:
        """
        Cambia el estado si la transición es válida.

        Las transiciones que el calendario tiene que conocer aumentan la
        secuencia, para que el .ics reemplace el evento anterior.
        """
        if not self.puede_pasar_a(estado):
            raise ValidationError(
                {
                    "estado": (
                        f"No se puede pasar de «{self.get_estado_display()}» a "
                        f"«{EstadoVisita(estado).label}»."
                    )
                },
                code="transicion_invalida",
            )

        self.estado = estado
        if motivo_rechazo:
            self.motivo_rechazo = motivo_rechazo

        if estado in (EstadoVisita.CONFIRMADA, EstadoVisita.CANCELADA):
            self.secuencia += 1

    def reprogramar(self, inicio, fin, posicion: int = 0) -> None:
        """Mueve la visita de bloque conservando su identificador de calendario."""
        if self.estado not in (EstadoVisita.SOLICITADA, EstadoVisita.CONFIRMADA):
            raise ValidationError(
                {"estado": "Solo se reprograma una visita solicitada o confirmada."},
                code="reprogramacion_invalida",
            )

        self.inicio = inicio
        self.fin = fin
        self.posicion = posicion
        self.secuencia += 1


class TipoCorreo(models.TextChoices):
    SOLICITUD_RECIBIDA = "solicitud_recibida", "Solicitud recibida"
    SOLICITUD_NUEVA = "solicitud_nueva", "Nueva solicitud para el dueño"
    CONFIRMADA = "confirmada", "Visita confirmada"
    RECHAZADA = "rechazada", "Visita rechazada"
    REPROGRAMADA = "reprogramada", "Visita reprogramada"
    CANCELADA = "cancelada", "Visita cancelada"
    RECORDATORIO = "recordatorio", "Recordatorio"


class EstadoEnvio(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    ENVIADO = "enviado", "Enviado"
    FALLIDO = "fallido", "Fallido"


class EnvioCorreo(ModeloDeTienda):
    """
    Registro de cada correo de la agenda.

    Una reserva nunca falla porque falló el correo: la visita se guarda igual,
    el fallo queda anotado acá y se reintenta después.
    """

    visita = models.ForeignKey(
        Visita,
        verbose_name="visita",
        on_delete=models.CASCADE,
        related_name="correos",
    )

    tipo = models.CharField("tipo", max_length=30, choices=TipoCorreo.choices)
    destinatario = models.EmailField("destinatario")

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=EstadoEnvio.choices,
        default=EstadoEnvio.PENDIENTE,
    )

    intentos = models.PositiveSmallIntegerField("intentos", default=0)
    ultimo_error = models.TextField("último error", blank=True)
    enviado_en = models.DateTimeField("enviado en", blank=True, null=True)

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "envío de correo"
        verbose_name_plural = "envíos de correo"
        ordering = ["-fecha_creacion"]
        indexes = [models.Index(fields=["estado"])]

    def __str__(self):
        estado = self.get_estado_display()
        return f"{self.get_tipo_display()} a {self.destinatario}: {estado}"
