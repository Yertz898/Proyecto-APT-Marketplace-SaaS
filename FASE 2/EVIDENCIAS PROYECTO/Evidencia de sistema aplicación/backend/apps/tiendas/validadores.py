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
