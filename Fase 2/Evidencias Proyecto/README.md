# Evidencias Proyecto — Fase 2

DealCommerce: marketplace SaaS multi-tienda con analítica predictiva para PYMES
del retail. Proyecto de título APT (PTY4614), Duoc UC.

**Equipo:** Pedro Santibáñez · Daniel Azócar
**Cliente piloto:** Joyas_ye

## Contenido

| Carpeta | Qué hay |
|---|---|
| `Evidencia de sistema aplicación/` | El código fuente completo del sistema: backend Django, frontend Next.js, contenedores y documentación. |
| `base de datos/` | El esquema PostgreSQL y los datos de demostración, con instrucciones para restaurarla. |

## Cómo levantarlo

Dentro de `Evidencia de sistema aplicación/`:

```bash
cp .env.example .env     # y completar los valores vacíos
docker compose up -d
```

El detalle está en el `README.md` de esa carpeta.

## Sobre los secretos y el `.gitignore`

Este repositorio es público, así que el proyecto se subió con su `.gitignore`
puesto. Lo que queda fuera **a propósito**:

- `.env` — contiene la clave secreta de Django y la contraseña de la base de
  datos. En su lugar va `.env.example`, con **los mismos nombres de variable y
  los valores vacíos**, para que se vea exactamente qué configuración necesita
  el sistema sin publicar ninguna credencial.
- `node_modules/`, `.next/`, `__pycache__/`, `staticfiles/` — se regeneran solos
  al instalar y compilar; no son fuente.
- `backend/media/` — archivos subidos por los usuarios.
- `/data/`, `*.pkl`, `*.joblib` — datos del cliente y modelos entrenados.

Nada de eso hace falta para revisar, instalar ni evaluar el sistema.

**Si la evaluación pide ver lo excluido**, el `.gitignore` está en la raíz de
`Evidencia de sistema aplicación/` y se puede ajustar. Antes de hacerlo conviene
tener presente dos cosas:

1. Quitar la regla de `.env` publicaría la clave secreta de Django y la
   contraseña de la base de datos de desarrollo. Si llega a pasar, esas dos
   credenciales hay que rotarlas, porque un repositorio público queda indexado.
2. Lo que se sube a un repositorio público **queda en el historial** aunque se
   borre después: para sacarlo de verdad hay que reescribir el historial y
   forzar el push.

La alternativa sin ese riesgo es entregar el `.env` por un canal privado a quien
lo solicite.

## Historial de desarrollo

La rama `desarrollo-fase-2` de este mismo repositorio tiene el historial
completo de commits con el que se construyó el sistema, por si la evaluación
considera el proceso y no solo el resultado.
