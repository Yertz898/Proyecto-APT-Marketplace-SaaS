FROM python:3.14-slim

# Salida sin búfer para ver los logs en tiempo real; sin .pyc en la imagen.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema mínimas para compilar e instalar los paquetes.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Qué dependencias entran a la imagen.
#
# Por omisión, solo las que hacen falta para servir. En desarrollo,
# docker-compose.yml pide `dev.txt`, que además trae pytest, ruff y la pila de
# analítica.
#
# La diferencia no es cosmética: `analitica.txt` arrastra xgboost, y xgboost
# arrastra las librerías CUDA de NVIDIA —351 MB solo una de ellas—. Una imagen
# de producción con eso adentro tarda en desplegarse, cuesta más de alojar y no
# ejecuta una sola línea de ese código.
ARG REQUIREMENTS=base.txt

# Las dependencias se copian antes que el código para aprovechar la caché de capas:
# cambiar un archivo .py no obliga a reinstalar todo.
COPY requirements/ requirements/
RUN pip install --upgrade pip && pip install -r "requirements/${REQUIREMENTS}"

COPY . .

EXPOSE 8000

# La imagen arranca lista para producción. En desarrollo, docker-compose.yml
# reemplaza este comando por `runserver`, que recarga al guardar un archivo.
#
# Al revés sería peor: la imagen quedaría con el servidor de desarrollo de
# Django adentro y cualquiera que la despliegue tal cual —Railway corre la
# imagen, no el compose— estaría sirviendo con él sin enterarse.
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60"]
