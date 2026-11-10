"""
Carga masiva del catálogo desde planillas.

Es por donde una tienda sube sus productos, sus tramos de precio y sus fotos.
No carga historial de ventas: el cliente no lo tiene con ese detalle.

No es una operación excepcional, es rutina: el catálogo rota seguido, así que
esto se usa tanto como el panel. Y es el módulo que más va a fallar, porque el
archivo lo hace una persona a mano.

De ahí las tres reglas que dan forma a esta tabla:

- **Nada se escribe en el catálogo hasta confirmar.** Una carga nace `validada`
  y solo entonces se aplica. Así el dueño ve qué va a pasar antes de que pase.
- **Una fila mala no bota a las demás.** Los rechazos se acumulan por número de
  fila en `errores` y el resto se aplica igual.
- **Lo que no viene en el archivo no se borra.** Se desactiva solo si el dueño
  lo marca: una planilla incompleta no puede vaciar una tienda.

El archivo original se guarda para poder auditar de dónde salió cada dato.
"""

import uuid

from django.db import models

from apps.core.models import ModeloDeTienda


class TipoCarga(models.TextChoices):
    PRODUCTOS = "productos", "Catálogo de productos"
    TRAMOS = "tramos", "Precios por volumen"
    FOTOS = "fotos", "Fotos de productos"


class EstadoCarga(models.TextChoices):
    VALIDADA = "validada", "Validada, sin aplicar"
    CONFIRMADA = "confirmada", "Confirmada"
    DESCARTADA = "descartada", "Descartada"


class Carga(ModeloDeTienda):
    """Un archivo subido, con lo que se decidió hacer con él."""

    # UUID y no autoincremental: el identificador viaja en la URL entre validar
    # y confirmar, y un número correlativo diría cuántas cargas lleva la
    # plataforma y dejaría probar las de al lado.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    usuario = models.ForeignKey(
        "usuarios.Usuario",
        verbose_name="quién subió el archivo",
        on_delete=models.PROTECT,
        related_name="cargas",
    )

    tipo = models.CharField("tipo", max_length=10, choices=TipoCarga.choices)

    archivo_original = models.FileField(
        "archivo subido", upload_to="cargas/", max_length=255
    )
    nombre_original = models.CharField(
        "nombre con que lo subieron",
        max_length=255,
        help_text=(
            "El nombre del sistema es otro; este es para que la persona lo "
            "reconozca."
        ),
    )

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=EstadoCarga.choices,
        default=EstadoCarga.VALIDADA,
    )

    creadas = models.PositiveIntegerField("filas nuevas", default=0)
    actualizadas = models.PositiveIntegerField("filas actualizadas", default=0)
    rechazadas = models.PositiveIntegerField("filas con error", default=0)

    #: Lista de {"fila": n, "motivo": "..."}.
    errores = models.JSONField("detalle de los rechazos", default=list, blank=True)

    #: Códigos que existen en la tienda y no venían en el archivo.
    ausentes = models.JSONField("códigos ausentes", default=list, blank=True)

    class Meta(ModeloDeTienda.Meta):
        verbose_name = "carga"
        verbose_name_plural = "cargas"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["tienda", "-fecha_creacion"]),
            models.Index(fields=["tienda", "tipo"]),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.nombre_original}"

    @property
    def pendiente(self) -> bool:
        """Validada y todavía sin aplicar: es la única que se puede confirmar."""
        return self.estado == EstadoCarga.VALIDADA

    def resultado(self) -> str:
        """
        Cómo terminó, en una línea, para el historial.

        Lo redacta el backend y no el navegador: el frontend muestra texto, no
        arma frases con cifras que podría leer al revés.
        """
        if self.estado == EstadoCarga.DESCARTADA:
            return "Descartada"

        if self.estado == EstadoCarga.VALIDADA:
            return f"Validada: {self.creadas} nuevos, {self.actualizadas} actualizados"

        partes = []
        if self.creadas:
            partes.append(f"{self.creadas} nuevos")
        if self.actualizadas:
            partes.append(f"{self.actualizadas} actualizados")
        if self.rechazadas:
            partes.append(f"{self.rechazadas} rechazados")

        return ", ".join(partes) if partes else "Sin cambios"
