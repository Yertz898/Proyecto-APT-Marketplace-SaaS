"""
Que la foto quede en una dirección que el navegador pueda abrir.

Un bucket de R2 nace privado y su endpoint S3 responde solo a peticiones
firmadas. Como las fotos del catálogo se piden sin firma —son públicas, no hace
falta firmarlas—, la dirección que sirve es la de un dominio conectado al
bucket, no la del endpoint. Esa diferencia no se nota en desarrollo, porque sin
R2 configurado las fotos salen del disco: se notaría recién en producción, con
la vitrina llena de imágenes rotas.

De ahí estas pruebas: una comprueba la traducción de la dirección del archivo de
entorno al par de valores que espera django-storages, y la otra comprueba que
ese par realmente cambia la dirección que entrega el almacenamiento.
"""

import os
import subprocess
import sys

import pytest
from django.conf import settings
from storages.backends.s3 import S3Storage

from config.almacenamiento import dominio_publico

ENDPOINT_PRIVADO = "https://cuenta.r2.cloudflarestorage.com"


@pytest.mark.parametrize(
    ("escrito", "esperado"),
    [
        # Lo normal: un dominio propio, con esquema.
        ("https://fotos.ejemplo.cl", ("fotos.ejemplo.cl", "https:")),
        # El subdominio que da Cloudflare, copiado sin esquema.
        ("pub-abc123.r2.dev", ("pub-abc123.r2.dev", "https:")),
        # La barra final dejaría la ruta con doble barra.
        ("https://fotos.ejemplo.cl/", ("fotos.ejemplo.cl", "https:")),
        # Un prefijo de ruta se conserva: el dominio puede servir otras cosas.
        ("https://cdn.ejemplo.cl/medios/", ("cdn.ejemplo.cl/medios", "https:")),
        # El protocolo no se fuerza: un proxy local puede servir por http.
        ("http://localhost:9000/bucket", ("localhost:9000/bucket", "http:")),
        # Espacios de más al copiar y pegar.
        ("  https://fotos.ejemplo.cl  ", ("fotos.ejemplo.cl", "https:")),
    ],
)
def test_la_direccion_se_parte_en_dominio_y_protocolo(escrito, esperado):
    assert dominio_publico(escrito) == esperado


def _almacenamiento(**opciones) -> S3Storage:
    """Un almacenamiento con las opciones de producción, sin llaves.

    Para armar la dirección de un archivo público no se necesita credencial
    alguna, así que acá no hay ninguna: la prueba no habla con R2.
    """
    return S3Storage(
        bucket_name="dealcommerce",
        endpoint_url=ENDPOINT_PRIVADO,
        region_name="auto",
        signature_version="s3v4",
        querystring_auth=False,
        **opciones,
    )


def test_sin_dominio_publico_la_foto_apunta_al_endpoint_privado():
    """El error que se está corrigiendo, escrito como prueba."""
    url = _almacenamiento().url("productos/anillo.jpg")

    assert url.startswith(ENDPOINT_PRIVADO)


def test_con_dominio_publico_la_foto_apunta_al_dominio():
    dominio, protocolo = dominio_publico("https://fotos.ejemplo.cl")

    url = _almacenamiento(custom_domain=dominio, url_protocol=protocolo).url(
        "productos/anillo.jpg"
    )

    assert url == "https://fotos.ejemplo.cl/productos/anillo.jpg"
    assert ENDPOINT_PRIVADO not in url


def test_configurar_r2_sin_dominio_publico_impide_arrancar():
    """
    Falta la variable y Django no levanta, en vez de servir enlaces rotos.

    Se prueba en otro proceso porque la configuración se arma una sola vez, al
    importarla.
    """
    entorno = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings",
        "R2_BUCKET_NAME": "dealcommerce",
        "R2_PUBLIC_BASE_URL": "",
    }

    resultado = subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=settings.BASE_DIR,
        env=entorno,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode != 0
    assert "R2_PUBLIC_BASE_URL" in resultado.stderr
