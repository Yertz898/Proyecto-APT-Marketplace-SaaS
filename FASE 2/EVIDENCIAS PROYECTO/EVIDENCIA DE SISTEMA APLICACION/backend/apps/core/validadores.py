"""
Validadores compartidos entre apps.

Acá va lo que más de una app necesita validar igual. El color hexadecimal, en
cambio, se queda en `tiendas` porque lo referencia una migración: moverlo
rompería el historial.
"""

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

#: Formatos que se aceptan para las imágenes que sube una tienda.
#:
#: Lista cerrada y corta a propósito. SVG queda fuera aunque sea una imagen:
#: es un documento XML que puede traer scripts, y todas las tiendas comparten
#: origen.
FORMATOS_DE_IMAGEN = {"JPEG", "PNG", "WEBP"}

#: Tope por archivo. Una foto razonable pesa mucho menos; el
#: límite está para que subir un archivo enorme no sea gratis.
TAMANO_MAXIMO_IMAGEN = 3 * 1024 * 1024


def validar_imagen(archivo):
    """
    Revisa una imagen por contenido y por tamaño.

    Por contenido y no por la extensión del nombre: la extensión la escribe
    quien sube el archivo y no dice nada de lo que hay adentro. Pillow abre el
    archivo y responde qué es en realidad.
    """
    if archivo.size > TAMANO_MAXIMO_IMAGEN:
        megas = TAMANO_MAXIMO_IMAGEN // (1024 * 1024)
        raise ValidationError(
            f"La imagen no puede pesar más de {megas} MB.",
            code="imagen_muy_grande",
        )

    try:
        with Image.open(archivo) as imagen:
            formato = imagen.format
            imagen.verify()
    except (UnidentifiedImageError, OSError) as error:
        raise ValidationError(
            "El archivo no es una imagen válida.", code="imagen_invalida"
        ) from error
    finally:
        # `Image.open` deja el puntero donde alcanzó a leer. Si no se devuelve
        # al principio, lo que se guarde después sale truncado.
        archivo.seek(0)

    if formato not in FORMATOS_DE_IMAGEN:
        aceptados = ", ".join(sorted(FORMATOS_DE_IMAGEN))
        raise ValidationError(
            f"El formato {formato} no se acepta. Usa {aceptados}.",
            code="formato_no_aceptado",
        )
