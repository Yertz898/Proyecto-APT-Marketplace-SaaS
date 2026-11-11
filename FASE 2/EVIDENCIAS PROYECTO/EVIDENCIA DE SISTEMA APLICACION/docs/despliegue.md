# Despliegue

Dónde vive cada parte en producción, qué variable necesita y en qué orden se levanta.

| Parte | Dónde | Por qué ahí |
|---|---|---|
| Frontend (Next.js) | Vercel | Es de quien hace Next; el build y las rutas dinámicas funcionan sin configurar nada |
| Backend (Django) | Railway | Corre la imagen de `backend/`, y la base de datos queda al lado |
| Base de datos | Railway (PostgreSQL) | Misma red interna que el backend: la conexión no sale a internet |
| Fotos de productos | Cloudflare R2 | El disco de un contenedor se borra en cada despliegue |
| Dominios | Cloudflare | Un nombre propio delante de los tres, para no depender de las URL que reparte cada servicio |

## Antes de empezar

Tres cosas que no son opcionales y que, si faltan, fallan **en producción y no antes**:

- **`DJANGO_DEBUG=False`.** Con `True`, Django muestra el detalle de cada error —rutas,
  configuración, fragmentos de código— a cualquiera que provoque uno.
- **`DJANGO_SECRET_KEY` nueva.** No la del `.env` local. Firma las sesiones y los tokens.
- **`NEXT_PUBLIC_MEDIA_URL` en el entorno de build de Vercel**, no solo en el de ejecución.
  Next la lee al compilar para la lista blanca del optimizador de imágenes. Si falta, las
  fotos no cargan y no hay ningún error que lo avise.

## Backend en Railway

La imagen de `backend/Dockerfile` ya arranca con gunicorn. El `runserver` que se usa en
desarrollo lo pone `docker-compose.yml` y no viaja a la imagen.

**La imagen por omisión instala solo `requirements/base.txt`**, que es lo que hace falta
para servir. `docker-compose.yml` pide `dev.txt` con un argumento de build, y ahí entran
pytest, ruff y la pila de analítica. La diferencia medida es **843 MB contra 2,53 GB**:
`analitica.txt` arrastra xgboost, y xgboost arrastra las librerías CUDA de NVIDIA, de las
que una sola pesa 351 MB. Si en algún momento los modelos entrenados corren dentro del
mismo proceso del backend, hay que desplegar con `--build-arg REQUIREMENTS=analitica.txt`
y contar con que la imagen triplica su tamaño.

Railway entrega el puerto en `$PORT`; el comando lo toma de ahí.

### Variables

Las mismas de `.env.example`, con estos valores:

```
DJANGO_SECRET_KEY=<una nueva, larga y al azar>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.tudominio.cl,<el host que da Railway>
DATABASE_URL=<la que inyecta el PostgreSQL de Railway>
CORS_ALLOWED_ORIGINS=https://tudominio.cl
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=...
R2_ENDPOINT_URL=https://<id-de-cuenta>.r2.cloudflarestorage.com
R2_PUBLIC_BASE_URL=https://fotos.tudominio.cl
```

`MEDIA_BASE_URL` no hace falta con R2 configurado: el almacenamiento ya entrega la
dirección pública de cada foto.

### En cada despliegue

```
python manage.py migrate
python manage.py collectstatic --noinput
```

`collectstatic` es para el admin de Django. Con `DEBUG=False` Django deja de servir
estáticos y de eso se encarga whitenoise, que necesita los archivos ya recogidos.

La primera vez, además:

```
python manage.py cargar_demo
python manage.py cuentas_demo
```

## Frontend en Vercel

Directorio raíz del proyecto: `FASE 2/EVIDENCIAS PROYECTO/EVIDENCIA DE SISTEMA APLICACION/frontend`.

```
NEXT_PUBLIC_API_URL=https://api.tudominio.cl/api
NEXT_PUBLIC_MEDIA_URL=https://fotos.tudominio.cl
```

Las dos tienen que estar marcadas para el entorno de **build**, no solo el de ejecución.

## El orden importa

1. **R2 primero**, con su dominio público conectado. El backend se niega a arrancar si hay
   `R2_BUCKET_NAME` sin `R2_PUBLIC_BASE_URL`, a propósito: un bucket de R2 nace privado y
   su endpoint exige firma, así que sin dominio público las fotos saldrían rotas y eso se
   descubriría mirando la vitrina.
2. **Backend después**, porque necesita las llaves de R2 y la base de datos.
3. **Frontend al final**, porque necesita la dirección del backend al compilar.
4. **Los dominios de Cloudflare**, y entonces volver a 2 y 3 para actualizar
   `DJANGO_ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` con los nombres definitivos.

El paso 4 obliga a volver atrás y no es un descuido de esta guía: hasta que el dominio
existe no se sabe qué nombre autorizar, y autorizar `*` mientras tanto deja la puerta
abierta a que cualquier sitio llame a la API con la sesión del comprador.

## Qué revisar cuando esté arriba

- La vitrina de `joyas-ye` carga **con fotos**. Sin fotos, el problema es
  `NEXT_PUBLIC_MEDIA_URL` o el dominio público de R2.
- El panel deja iniciar sesión. Si el navegador bloquea la petición, es
  `CORS_ALLOWED_ORIGINS`.
- El admin de Django se ve con estilos. Sin estilos, faltó `collectstatic`.
- Un pedido de prueba de punta a punta: agregar al carrito, confirmar, verlo en la bandeja.

## Lo que no está resuelto

- **No hay copias de seguridad automáticas** de la base. Railway ofrece las suyas; hay que
  activarlas.
- **No hay un entorno de prueba aparte.** Lo que se despliega va directo a lo que ve el
  cliente.
- **El historial de ventas del cliente no se despliega.** Vive en `data/`, fuera del
  repositorio, y se importa a mano donde haga falta. En producción eso significa que el
  pronóstico y los segmentos no tienen datos hasta que alguien corra `importar_historial`
  contra esa base.
