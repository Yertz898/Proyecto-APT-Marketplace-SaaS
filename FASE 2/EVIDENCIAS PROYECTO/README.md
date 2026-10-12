# Evidencias Proyecto — Fase 2

DealCommerce: marketplace SaaS multi-tienda con analítica predictiva para PYMES del
retail. Proyecto de título APT (PTY4614), Duoc UC.

Equipo: Pedro Santibáñez y Daniel Azócar.
Cliente piloto: Joyas_ye.

## Contenido

- `Evidencia de sistema aplicación/`: el código fuente del sistema. Backend Django,
  frontend Next.js, contenedores y documentación.
- `base de datos/`: el esquema PostgreSQL y los datos de demostración, con instrucciones
  para restaurarla.

## Cómo levantarlo

Dentro de `Evidencia de sistema aplicación/`:

```bash
cp .env.example .env     # completar los valores
docker compose up -d
```

El detalle está en el `README.md` de esa carpeta.

## Qué no está en el repositorio

El repositorio es público, así que el proyecto se subió con su `.gitignore`. Queda fuera:

- `.env`, que tiene la clave secreta de Django y la contraseña de la base de datos. En su
  lugar está `.env.example`, con los mismos nombres de variable y los valores vacíos.
- `node_modules/`, `.next/`, `__pycache__/` y `staticfiles/`, que se regeneran al
  instalar y compilar.
- `backend/media/`, con los archivos que suben los usuarios.
- `/data/`, `*.pkl` y `*.joblib`: datos del cliente y modelos entrenados.

Nada de eso hace falta para instalar ni para evaluar el sistema. Si se necesita el `.env`,
se entrega por un canal privado: publicarlo en un repositorio público obligaría a rotar
esas credenciales.
