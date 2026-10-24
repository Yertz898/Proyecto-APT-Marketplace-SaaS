"""
Los endpoints de la carga masiva.

El recorrido es el mismo para los tres tipos y es deliberado: **validar,
mirar, confirmar**. Entre el primer paso y el último no se escribe una sola
fila del catálogo, porque el archivo lo hizo una persona a mano y conviene que
vea qué va a pasar antes de que pase.

La tienda sale del token en todos. Una carga de otra tienda responde 404: el
identificador viaja en la URL entre validar y confirmar.
"""

from django.conf import settings
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import MixinTiendaDelUsuario
from apps.core.permissions import TrabajaEnLaTienda
from apps.ingesta import fotos as fotos_zip
from apps.ingesta import planillas, plantillas
from apps.ingesta import productos as carga_productos
from apps.ingesta import tramos as carga_tramos
from apps.ingesta.models import Carga, EstadoCarga, TipoCarga
from apps.ingesta.serializers import CargaDelHistorialSerializer

#: Qué extensiones se ofrecen en la pantalla, por tipo de carga.
EXTENSIONES = {
    TipoCarga.PRODUCTOS: [".xlsx", ".csv"],
    TipoCarga.TRAMOS: [".xlsx", ".csv"],
    TipoCarga.FOTOS: [".zip"],
}


class LimitesDeCarga(generics.GenericAPIView):
    """
    Qué acepta el backend.

    La pantalla lo pregunta en vez de llevarlo escrito, para que el aviso de
    «pesa demasiado» salga antes de subir y no después de esperar.
    """

    permission_classes = [TrabajaEnLaTienda]

    def get(self, request):
        return Response(
            {
                "extensiones": sorted(
                    {e for lista in EXTENSIONES.values() for e in lista}
                ),
                "tamanoMaximoBytes": settings.TAMANO_MAXIMO_CARGA,
            }
        )


class PlantillaDeCarga(generics.GenericAPIView):
    """La planilla vacía, con los encabezados exactos y una fila de ejemplo."""

    permission_classes = [TrabajaEnLaTienda]

    def get(self, request, tipo):
        if tipo not in plantillas.COLUMNAS:
            raise ValidationError({"tipo": "No hay plantilla para ese tipo de carga."})

        respuesta = HttpResponse(
            plantillas.construir(tipo),
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        respuesta["Content-Disposition"] = (
            f'attachment; filename="plantilla-{tipo}.xlsx"'
        )
        return respuesta


class ValidarCarga(MixinTiendaDelUsuario, generics.GenericAPIView):
    """
    Revisa el archivo y **no escribe nada en el catálogo**.

    Deja una `Carga` en estado `validada` con el resumen adentro. Lo que se
    guarda en este paso es el archivo subido y la decisión tomada sobre cada
    fila; el catálogo se toca recién al confirmar.
    """

    permission_classes = [TrabajaEnLaTienda]
    queryset = Carga.objects.all()

    def post(self, request, tipo):
        if tipo not in TipoCarga.values:
            raise ValidationError({"tipo": "Ese tipo de carga no existe."})

        archivo = self._archivo(request)
        tienda = request.user.tienda

        try:
            if tipo == TipoCarga.FOTOS:
                resumen = fotos_zip.revisar(tienda, archivo)
            else:
                filas = planillas.leer(archivo)
                revisor = (
                    carga_productos if tipo == TipoCarga.PRODUCTOS else carga_tramos
                )
                resumen = revisor.revisar(tienda, filas)
        except planillas.ArchivoInvalido as error:
            raise ValidationError({"archivo": str(error)}) from error

        carga = self._guardar(request, tipo, archivo, resumen)
        return Response(
            self._resumen(tipo, carga, resumen), status=status.HTTP_201_CREATED
        )

    def _archivo(self, request):
        archivo = request.FILES.get("archivo")
        if archivo is None:
            raise ValidationError({"archivo": "Elige un archivo."})

        if archivo.size > settings.TAMANO_MAXIMO_CARGA:
            megas = settings.TAMANO_MAXIMO_CARGA // (1024 * 1024)
            raise ValidationError(
                {"archivo": f"El archivo no puede pesar más de {megas} MB."}
            )

        return archivo

    def _guardar(self, request, tipo, archivo, resumen) -> Carga:
        """
        Deja constancia de lo que se revisó.

        El nombre original se guarda aparte del archivo: el del sistema es otro,
        y la persona reconoce el suyo en el historial.
        """
        comunes = {
            "tienda": request.user.tienda,
            "usuario": request.user,
            "tipo": tipo,
            "archivo_original": archivo,
            "nombre_original": archivo.name[:255],
            "rechazadas": len(getattr(resumen, "rechazos", [])),
            "errores": getattr(resumen, "rechazos", []),
        }

        if tipo == TipoCarga.FOTOS:
            comunes["creadas"] = resumen.emparejadas
        else:
            comunes["creadas"] = resumen.crear
            comunes["actualizadas"] = resumen.actualizar
            comunes["ausentes"] = getattr(resumen, "ausentes", [])

        return Carga.objects.create(**comunes)

    def _resumen(self, tipo, carga, resumen) -> dict:
        if tipo == TipoCarga.FOTOS:
            return {
                "cargaId": str(carga.id),
                "emparejadas": resumen.emparejadas,
                "productosSinFoto": resumen.productos_sin_foto,
                "fotosSinProducto": resumen.fotos_sin_producto,
            }

        return {
            "cargaId": str(carga.id),
            "crear": resumen.crear,
            "actualizar": resumen.actualizar,
            "rechazar": resumen.rechazar,
            "rechazos": resumen.rechazos,
            "ausentes": getattr(resumen, "ausentes", []),
        }


class ConfirmarCarga(MixinTiendaDelUsuario, generics.GenericAPIView):
    """
    Aplica una carga ya validada. Es el único paso que escribe en el catálogo.

    Se vuelve a leer el archivo guardado en vez de confiar en lo que mandó el
    navegador: entre validar y confirmar pasa tiempo, y lo que se aplica tiene
    que ser lo que se revisó.
    """

    permission_classes = [TrabajaEnLaTienda]
    queryset = Carga.objects.all()
    lookup_field = "id"

    def post(self, request, id):  # noqa: A002 — lo fija la ruta
        carga = self.get_object()

        if not carga.pendiente:
            raise ValidationError(
                {"carga": "Esta carga ya se aplicó o se descartó."}
            )

        desactivar = bool(request.data.get("desactivarAusentes"))
        tienda = request.user.tienda

        with carga.archivo_original.open("rb") as archivo:
            if carga.tipo == TipoCarga.FOTOS:
                resumen = fotos_zip.revisar(tienda, archivo)
                creadas = fotos_zip.aplicar(archivo, resumen)
                actualizadas = 0
            elif carga.tipo == TipoCarga.PRODUCTOS:
                resumen = carga_productos.revisar(tienda, planillas.leer(archivo))
                creadas, actualizadas = carga_productos.aplicar(
                    tienda, resumen, desactivar
                )
            else:
                resumen = carga_tramos.revisar(tienda, planillas.leer(archivo))
                creadas, actualizadas = carga_tramos.aplicar(tienda, resumen)

        carga.estado = EstadoCarga.CONFIRMADA
        carga.creadas = creadas
        carga.actualizadas = actualizadas
        carga.save(update_fields=["estado", "creadas", "actualizadas"])

        return Response({"creadas": creadas, "actualizadas": actualizadas})


class DescartarCarga(MixinTiendaDelUsuario, generics.DestroyAPIView):
    """
    Descarta una carga validada.

    No se borra la fila: queda como `descartada`. El historial tiene que poder
    mostrar también lo que se decidió no aplicar.
    """

    permission_classes = [TrabajaEnLaTienda]
    queryset = Carga.objects.all()
    lookup_field = "id"

    def perform_destroy(self, carga):
        if not carga.pendiente:
            raise ValidationError({"carga": "Esta carga ya se aplicó."})

        carga.estado = EstadoCarga.DESCARTADA
        carga.save(update_fields=["estado"])


class HistorialDeCargas(MixinTiendaDelUsuario, generics.ListAPIView):
    """Qué se cargó, cuándo y quién. Para poder auditar de dónde salió un dato."""

    serializer_class = CargaDelHistorialSerializer
    permission_classes = [TrabajaEnLaTienda]
    pagination_class = None
    queryset = Carga.objects.all()

    def get_queryset(self):
        cargas = super().get_queryset().select_related("usuario")

        tipo = self.request.query_params.get("tipo")
        if tipo:
            cargas = cargas.filter(tipo=tipo)

        return cargas[:50]
