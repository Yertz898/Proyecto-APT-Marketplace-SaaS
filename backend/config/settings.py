"""
Configuración de Django para DealCommerce.

Toda credencial y todo valor que cambie entre ambientes se lee de variables de
entorno. El repositorio es público: acá no se escribe ningún secreto, ni siquiera
como valor por omisión.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DJANGO_TIME_ZONE=(str, "America/Santiago"),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000"]),
    JWT_ACCESS_TOKEN_LIFETIME_MINUTES=(int, 60),
    JWT_REFRESH_TOKEN_LIFETIME_DAYS=(int, 7),
    R2_BUCKET_NAME=(str, ""),
)

# Fuera de Docker, .env vive en la raíz del repositorio.
environ.Env.read_env(BASE_DIR.parent / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")


# ── Aplicaciones ────────────────────────────────────────────────────────────

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "storages",
]

# El orden importa: `core` define la capa común de aislamiento por tienda que el
# resto de las apps consume, y `tiendas` define la raíz de ese aislamiento.
LOCAL_APPS = [
    "apps.core",
    "apps.usuarios",
    "apps.tiendas",
    "apps.catalogo",
    "apps.precios",
    "apps.pedidos",
    "apps.clientes",
    "apps.ingesta",
    "apps.analitica",
    "apps.asistente",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ── Base de datos ───────────────────────────────────────────────────────────
# PostgreSQL. El esquema se versiona con migraciones de Django, nunca con SQL suelto.

DATABASES = {"default": env.db("DATABASE_URL")}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Modelo de usuario propio desde el inicio: cambiarlo después obliga a rehacer
# las migraciones de todo el proyecto. La cuenta se identifica por correo.
AUTH_USER_MODEL = "usuarios.Usuario"


# ── Contraseñas ─────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ── API ─────────────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Cerrado por omisión: un endpoint nuevo exige autenticación aunque el autor
    # olvide declararlo. Abrir explícitamente el que deba ser público.
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}

from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env("JWT_ACCESS_TOKEN_LIFETIME_MINUTES")
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env("JWT_REFRESH_TOKEN_LIFETIME_DAYS")),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
}

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")


# ── Internacionalización ────────────────────────────────────────────────────

LANGUAGE_CODE = "es-cl"
TIME_ZONE = env("DJANGO_TIME_ZONE")
USE_I18N = True
USE_TZ = True


# ── Archivos estáticos y de medios ──────────────────────────────────────────
# Las imágenes de producto van a Cloudflare R2 (API compatible con S3).
# La base de datos guarda solo la referencia, nunca el binario.

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if env("R2_BUCKET_NAME"):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": env("R2_BUCKET_NAME"),
                "access_key": env("R2_ACCESS_KEY_ID"),
                "secret_key": env("R2_SECRET_ACCESS_KEY"),
                "endpoint_url": env("R2_ENDPOINT_URL"),
                "region_name": "auto",
                "signature_version": "s3v4",
                "querystring_auth": False,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
else:
    # Sin R2 configurado (desarrollo temprano, CI) se guarda en disco local.
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"


# ── Seguridad ───────────────────────────────────────────────────────────────
# Se endurece sola cuando DEBUG está apagado, para que el ambiente de pruebas y
# el de producción no dependan de que alguien recuerde activarlo.

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"
