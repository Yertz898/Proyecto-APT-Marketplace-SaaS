# DealCommerce

Marketplace SaaS multi-tienda con analítica predictiva para PYMES del retail.
Proyecto de título, Capstone PTY4614, Duoc UC.

Las reglas del proyecto (aislamiento entre tiendas, alcance, convenciones) están en
[CONVENCIONES.md](CONVENCIONES.md). Acá solo está cómo levantar y trabajar el repositorio.

## Puesta en marcha

Requisitos: Docker Desktop y Git. Node y Python solo hacen falta para trabajar fuera de
los contenedores.

```bash
git clone <url-del-repositorio>
cd dealcommerce
cp .env.example .env      # completar los valores; .env nunca se versiona
docker compose up -d
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser
```

Para desarrollo local, poner `DJANGO_DEBUG=True` en el `.env`.

| Servicio | URL | Qué es |
|---|---|---|
| `web` | http://localhost:3000 | Frontend Next.js |
| `api` | http://localhost:8000 | Backend Django REST Framework |
| `db` | localhost:5432 | PostgreSQL 17 |

## Comandos

```bash
docker compose up -d                            # levanta todo
docker compose down                             # detiene todo
docker compose logs -f api                      # logs del backend

docker compose exec api pytest                  # pruebas del backend
docker compose exec api pytest -m aislamiento   # solo pruebas de aislamiento
docker compose exec api ruff check .            # lint del backend
docker compose exec api ruff format .           # formato del backend

docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate

docker compose exec web npm run lint            # lint del frontend
```

## Estructura

```
.
├── backend/                  Django + Django REST Framework
│   ├── config/               settings, urls y wsgi
│   ├── apps/
│   │   ├── core/             aislamiento por tienda y permisos por rol
│   │   ├── usuarios/         cuentas, roles y autenticación JWT
│   │   ├── tiendas/          Tienda, la raíz del aislamiento
│   │   ├── catalogo/         lotes y líneas de granel
│   │   ├── precios/          tramos de precio para lotes y granel
│   │   ├── pedidos/          pedidos con checkout simulado
│   │   ├── clientes/         compradores y variables RFM
│   │   ├── ingesta/          carga masiva del catálogo desde planillas
│   │   ├── analitica/        pronóstico, segmentación y reglas de descuento
│   │   ├── agenda/           agenda de visitas a la tienda
│   │   └── asistente/        asistente conversacional del vendedor
│   ├── requirements/         base.txt, analitica.txt, dev.txt
│   └── tests/                pruebas transversales
├── frontend/                 Next.js + Tailwind + shadcn/ui
├── docs/                     documentación del proyecto
├── infra/                    scripts de infraestructura
└── docker-compose.yml
```

## Trabajar fuera de Docker

Hay un entorno local para que el editor tenga autocompletado y para correr comandos
sueltos sin levantar contenedores.

```bash
# Backend (Windows / PowerShell)
backend\.venv\Scripts\Activate.ps1
cd backend
python manage.py runserver

# Frontend
cd frontend
npm run dev
```

Corriendo Django fuera de Docker, `DATABASE_URL` apunta a `localhost:5432` en vez de
`db:5432`. Es la única diferencia entre los dos modos.

## Flujo de trabajo

Rama por funcionalidad, nunca commits directos a `main`. Pull request revisado por el
otro integrante antes de integrar. Mensajes de commit en español y en imperativo.

```bash
git switch -c precios/motor-por-tramos
git commit -m "agrega motor de precios por tramos"
```

La plantilla de pull request ([.github/pull_request_template.md](.github/pull_request_template.md))
incluye el criterio de terminado y la verificación de aislamiento por tienda.

El aislamiento entre tiendas no se implementa dos veces: la capa común vive en
`backend/apps/core/` y el resto de las apps la usa. Toda funcionalidad que lea datos de
tienda lleva su prueba marcada con `@pytest.mark.aislamiento`.

## Los dos accesos

El sistema tiene dos entradas distintas y no se mezclan.

| | DealCommerce | Cada tienda |
|---|---|---|
| Dirección | `/panel/entrar` | `/t/<slug>/entrar` |
| Para quién | Administración de la plataforma, dueños y vendedores | Quien compra en esa tienda |
| Aspecto | La marca de DealCommerce | La identidad de esa tienda |
| Crear cuenta | No: las crea la plataforma | Sí |
| A dónde llega | `/plataforma` el administrador, `/panel` la tienda | La tienda donde estaba |

Para tener cuentas con las que probar:

```bash
docker compose exec api python manage.py cuentas_demo
```

Crea tres: administrador de plataforma, dueño de la tienda y compradora. Se puede correr
las veces que haga falta. La contraseña sale de `DEMO_PASSWORD`; si esa variable no está
definida, el comando genera una al azar y la muestra al terminar. Son cuentas de
demostración y no deben existir en producción.

## API

Todo cuelga de `/api`.

| Método | Ruta | Quién |
|---|---|---|
| `POST` | `/api/auth/sesion` | cualquiera |
| `POST` | `/api/auth/sesion/renovar` | cualquiera |
| `POST` | `/api/auth/registro` | cualquiera (crea compradores) |
| `GET` | `/api/auth/yo` | con sesión |
| `GET` | `/api/t/<slug>/tienda` | público |
| `GET` | `/api/t/<slug>/lotes` | público |
| `GET` | `/api/t/<slug>/lotes/<codigo>` | público |
| `GET` | `/api/t/<slug>/granel` | público |
| `GET` | `/api/t/<slug>/granel/<codigo>` | público |
| `GET` | `/api/t/<slug>/agenda/horas` | público |
| `POST` | `/api/t/<slug>/agenda/visitas` | comprador |
| `GET` | `/api/panel/tienda` | dueño o vendedor |
| `PATCH` | `/api/panel/tienda` | solo el dueño |
| `POST` | `/api/solicitudes-de-acceso` | cualquiera |

Las rutas `/t/<slug>/` sacan la tienda del slug y son públicas. Las de `/panel/` la sacan
del **token**, y por eso no la nombran: no existe la petición que pida los datos de otra
tienda. El detalle de cada una está en [docs/api.md](docs/api.md).

Las tres rutas de sesión comparten un límite de intentos por IP
(`THROTTLE_AUTENTICACION`). Las solicitudes de acceso tienen el suyo
(`THROTTLE_SOLICITUDES`).

Los errores tienen siempre la misma forma, con el mensaje en español:

```json
{"error": {"codigo": "validacion", "mensaje": "Revisa los datos marcados.",
           "detalles": {"email": ["Ya hay una cuenta con este correo."]}}}
```

## Datos para probar

```bash
docker compose exec api python manage.py cargar_demo
```

Deja el catálogo de Joyas_ye: 7 categorías, 5 líneas de granel con los precios reales que
entregó el cliente y 6 lotes de ejemplo que lo dicen en el nombre. Es idempotente y no
repone los cupos ya vendidos.

## Estado

Funcionan de punta a punta la portada con su solicitud de acceso, la identidad pública de
la tienda, el catálogo de lotes y granel, la agenda de visitas, la sesión con sus tres
pantallas y el perfil de la tienda desde el panel.

Pendiente: el carrito y los pedidos, la carga masiva de catálogo, el catálogo y los precios
editables desde el panel, el equipo y toda la analítica. Las pantallas de esas partes ya
existen y dicen que no están conectadas en vez de mostrar números inventados.

De la agenda falta la bandeja del dueño para aceptar o rechazar visitas, los correos con
archivo `.ics` y el recordatorio de 24 horas.
