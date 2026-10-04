"""Validadores de la identidad visual de una tienda."""

from django.core.validators import RegexValidator

#: Los colores de la tienda se aplican como variables CSS en el frontend. Solo
#: se acepta hexadecimal de seis dígitos: cualquier otra cosa podría colarse
#: como CSS arbitrario en una página que comparten todas las tiendas.
validar_color_hexadecimal = RegexValidator(
    regex=r"^#[0-9a-fA-F]{6}$",
    message="El color debe ser hexadecimal de seis dígitos, como #7C3AED.",
    code="color_invalido",
)


#: Formatos que se aceptan para el logo y el banner.
#:
#: Lista cerrada y corta a propósito. SVG queda fuera aunque sea una imagen:
#: es un documento XML que puede traer scripts, y todas las tiendas comparten
#: origen.
FORMATOS_DE_IMAGEN = {"JPEG", "PNG", "WEBP"}

#: Tope por archivo. Un logo o un banner razonables pesan mucho menos; el
#: límite está para que subir un archivo enorme no sea gratis.
TAMANO_MAXIMO_IMAGEN = 3 * 1024 * 1024


def validar_imagen_de_marca(archivo):
    """
    Revisa una imagen de la tienda por contenido y por tamaño.

    Por contenido y no por la extensión del nombre: la extensión la escribe
    quien sube el archivo y no dice nada de lo que hay adentro. Pillow abre el
    archivo y responde qué es en realidad.
    """
    from django.core.exceptions import ValidationError
    from PIL import Image, UnidentifiedImageError

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
