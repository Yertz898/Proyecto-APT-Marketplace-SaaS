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

# Las dependencias se copian antes que el código para aprovechar la caché de capas:
# cambiar un archivo .py no obliga a reinstalar todo.
COPY requirements/ requirements/
RUN pip install --upgrade pip && pip install -r requirements/dev.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
