"""
Cómo se arma la dirección pública de una imagen.

Estaba repetido en cuatro serializadores y con un error de fondo: se resolvía
con `build_absolute_uri`, es decir, **con el host de quien preguntó**. Desde el
navegador salía `localhost:8000` y desde el servidor de Next, que vive en otro
contenedor, salía `api:8000`, que ningún navegador resuelve. La misma foto
llegaba con dos direcciones según quién la pidiera, y una de las dos no cargaba.

La dirección de una imagen no depende de quién la pide. Sale de la
configuración: en producción la entrega R2 ya absoluta, y en desarrollo se le
antepone `MEDIA_BASE_URL`, que apunta al puerto por donde el navegador alcanza
a Django.
"""

from django.conf import settings


def url_publica(archivo) -> str | None:
    """La dirección con que un navegador puede pedir este archivo."""
    if not archivo:
        return None

    url = archivo.url

    # Con R2 configurado, el almacenamiento ya devuelve la dirección completa.
    if url.startswith(("http://", "https://")):
        return url

    base = getattr(settings, "MEDIA_BASE_URL", "")
    return f"{base.rstrip('/')}{url}" if base else url


def imagen(archivo, alt: str) -> dict | None:
    """
    Una imagen con la forma que espera el frontend, o `None` si no hay.

    Null y no un marcador: una imagen vacía se confunde con una que no cargó.
    """
    url = url_publica(archivo)
    return {"url": url, "alt": alt} if url else None
