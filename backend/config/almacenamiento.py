"""
Cómo se publica una foto guardada en Cloudflare R2.

Un bucket de R2 nace privado y su endpoint S3 exige firma, así que la dirección
que devuelve el almacenamiento no la puede abrir un navegador. Para que la foto
cargue en la vitrina hay que servirla por un dominio público: uno propio
conectado al bucket, o el subdominio `r2.dev` que ofrece Cloudflare. Eso es lo
que django-storages llama `custom_domain`.

Ese parámetro no recibe una URL. El almacenamiento arma la dirección como
`<protocolo>//<dominio>/<ruta>`, de modo que el esquema viaja aparte y una barra
final dejaría la ruta con doble barra. Acá se traduce lo que se escribe en el
archivo de entorno, que es una dirección normal, a ese par de valores.
"""

from urllib.parse import urlsplit

PROTOCOLO_POR_OMISION = "https"


def dominio_publico(base: str) -> tuple[str, str]:
    """
    Parte una dirección pública en el dominio y el protocolo que espera
    django-storages.

    Acepta la dirección con esquema o sin él y con o sin barra final, y conserva
    el prefijo de ruta cuando el dominio sirve las fotos bajo una carpeta.
    """
    base = base.strip()
    if "//" not in base:
        # Sin esquema, `urlsplit` leería el dominio como una ruta.
        base = f"//{base}"

    partes = urlsplit(base, scheme=PROTOCOLO_POR_OMISION)
    dominio = f"{partes.netloc}{partes.path}".rstrip("/")
    return dominio, f"{partes.scheme}:"
