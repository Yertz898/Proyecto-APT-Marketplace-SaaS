# DealCommerce

Marketplace SaaS multi-tienda con analítica predictiva para PYMES del retail.
Proyecto de título — Capstone PTY4614, Duoc UC.

Las reglas del proyecto (invariante de aislamiento, alcance, convenciones) están en
[CONVENCIONES.md](CONVENCIONES.md). Este archivo solo explica cómo levantar y trabajar el repositorio.

---

## Puesta en marcha

Requisitos: Docker Desktop, Git. (Node y Python solo hacen falta para trabajar fuera
de los contenedores.)

```bash
git clone <url-del-repositorio>
cd dealcommerce
cp .env.example .env      # completar los valores; .env nunca se versiona
                          # para desarrollo local: DJANGO_DEBUG=True en tu .env
docker compose up -d
```

Servicios:

| Servicio | URL | Descripción |
|---|---|---|
| `web` | http://localhost:3000 | Frontend Next.js |
| `api` | http://localhost:8000 | Backend Django REST Framework |
| `db`  | localhost:5432 | PostgreSQL 17 |

> **No ejecutar `migrate` todavía.** Primero hay que definir el modelo `Usuario` en
> `apps/usuarios` y activar `AUTH_USER_MODEL` en `config/settings.py`. Si se migra antes,
> Django crea las tablas con su usuario por defecto y cambiarlo después obliga a borrar la
> base de datos.

Una vez definido `Usuario`, el primer arranque es:

```bash
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser
```

## Comandos

```bash
docker compose up -d                                    # levanta todo
docker compose down                                     # detiene todo
docker compose logs -f api                              # logs del backend

docker compose exec api pytest                          # pruebas del backend
docker compose exec api pytest -m aislamiento           # solo pruebas de aislamiento
docker compose exec api ruff check .                    # lint del backend (PEP 8)
docker compose exec api ruff format .                   # formato del backend

docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate

docker compose exec web npm run lint                    # lint del frontend
```

## Estructura

```
.
├── backend/                  Django + Django REST Framework
│   ├── config/               settings, urls y wsgi del proyecto
│   ├── apps/                 aplicaciones del dominio
│   │   ├── core/             capa común: aislamiento por tienda y permisos por rol
│   │   ├── usuarios/         cuentas, roles y autenticación JWT
│   │   ├── tiendas/          Tienda — la raíz del aislamiento
│   │   ├── catalogo/         productos y variantes (el stock vive en la variante)
│   │   ├── precios/          listas de precios escalonados por volumen
│   │   ├── pedidos/          pedidos con checkout simulado
│   │   ├── clientes/         clientes compradores y variables RFM
│   │   ├── ingesta/          carga del historial de ventas desde planillas
│   │   ├── analitica/        pronóstico, segmentación y reglas de descuento
│   │   └── asistente/        asistente conversacional del vendedor
│   ├── requirements/         base.txt · analitica.txt · dev.txt
│   └── tests/                pruebas transversales
├── frontend/                 Next.js + Tailwind + shadcn/ui
├── docs/                     documentación del proyecto
├── infra/                    scripts e inicialización de infraestructura
└── docker-compose.yml
```

## Trabajar fuera de Docker

Hay un entorno local preparado para que el editor tenga autocompletado y para correr
comandos sueltos sin levantar contenedores.

```bash
# Backend (Windows / PowerShell)
backend\.venv\Scripts\Activate.ps1
cd backend
python manage.py runserver

# Frontend
cd frontend
npm run dev
```

Al correr Django fuera de Docker, `DATABASE_URL` debe apuntar a `localhost:5432` en vez
de `db:5432`. Es la única diferencia entre los dos modos.

## Flujo de trabajo

Rama por funcionalidad, nunca commits directos a `main`. Pull request revisado por el otro
integrante antes de integrar. Mensajes de commit en español y en imperativo.

```bash
git switch -c precios/motor-escalonado
git commit -m "agrega motor de precios escalonados"
```

La plantilla de pull request ([.github/pull_request_template.md](.github/pull_request_template.md))
incluye la lista del criterio de terminado y la verificación de aislamiento por tienda.

## Antes de escribir código que lea datos de tienda

El aislamiento entre tiendas es el invariante del sistema y no se implementa dos veces.
La capa común vive en `backend/apps/core/`; el resto de las apps la usa, no la reimplementa.
Toda funcionalidad que lea datos de tienda lleva su prueba de aislamiento marcada con
`@pytest.mark.aislamiento`.

## API

Todo cuelga de `/api`. Lo que existe hoy:

| Método | Ruta | Quién |
|---|---|---|
| `POST` | `/api/auth/sesion` | cualquiera |
| `POST` | `/api/auth/sesion/renovar` | cualquiera |
| `POST` | `/api/auth/registro` | cualquiera (crea compradores) |
| `GET` | `/api/auth/yo` | con sesión |
| `GET` | `/api/t/<slug>/tienda` | público |
| `GET` | `/api/t/<slug>/agenda/horas` | público |
| `POST` | `/api/t/<slug>/agenda/visitas` | comprador |
| `POST` | `/api/solicitudes-de-acceso` | cualquiera |

Las tres de sesión comparten un límite de intentos por IP
(`THROTTLE_AUTENTICACION`); las solicitudes de acceso tienen el suyo
(`THROTTLE_SOLICITUDES`).

Un error siempre tiene la misma forma, con el mensaje ya redactado en español:

```json
{"error": {"codigo": "validacion", "mensaje": "Revisa los datos marcados.",
           "detalles": {"email": ["Ya hay una cuenta con este correo."]}}}
```

## Estado

En construcción. Funcionan de punta a punta la portada con su solicitud de acceso,
la identidad pública de la tienda, la agenda de visitas (ver horas y reservar) y la
sesión con sus tres pantallas.

La portada (`/`) es la única parte del sitio con la marca de la plataforma: paleta
clara, Plus Jakarta Sans e Inter. La vitrina de cada tienda se ve como esa tienda
quiera, y por eso no comparten ni un componente.

Pendiente: el catálogo de lotes y granel, el carrito y los pedidos, la ingesta de
planillas y la analítica. Las pantallas de esas partes ya están hechas contra
clientes de API que todavía no tienen endpoint detrás.

Pendientes conocidos de la agenda: la bandeja del dueño para aceptar o rechazar
visitas, los correos con el archivo `.ics` y el recordatorio de 24 horas.
