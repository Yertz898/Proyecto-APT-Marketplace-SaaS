"""Validación de RUT chileno."""

import re

from django.core.exceptions import ValidationError

FORMATO = re.compile(r"^\d{7,8}-[\dK]$")


def normalizar_rut(valor: str) -> str:
    """
    Deja el RUT en la forma canónica 12345678-5: sin puntos, sin espacios y con
    la K en mayúscula. Se guarda siempre así para que un mismo RUT no entre dos
    veces escrito distinto.
    """
    return valor.replace(".", "").replace(" ", "").upper()


def digito_verificador(cuerpo: str) -> str:
    """Dígito verificador por módulo 11."""
    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def validar_rut(valor: str) -> None:
    """Valida formato y dígito verificador. Se usa como validador del campo."""
    rut = normalizar_rut(valor)

    if not FORMATO.match(rut):
        raise ValidationError(
            "El RUT debe tener la forma 12345678-5, sin puntos y con guion.",
            code="rut_formato",
        )

    cuerpo, verificador = rut.split("-")
    if digito_verificador(cuerpo) != verificador:
        raise ValidationError(
            "El dígito verificador del RUT no corresponde.", code="rut_invalido"
        )
