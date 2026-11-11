# Base de datos

PostgreSQL 17. El esquema se versiona con migraciones de Django; estos archivos son una
foto de la base para poder revisarla y restaurarla sin levantar el proyecto entero.

- `01-estructura.sql`: tablas, llaves foráneas, restricciones, índices y secuencias. Sin
  filas.
- `02-datos-demo.sql`: los datos de demostración. Las dos tiendas de ejemplo con su
  catálogo —noventa y cinco productos, once categorías y diecinueve tramos de precio—, la
  configuración de agenda con sus diez bloques de atención, y las tablas internas de
  Django.

## Restaurarla

```bash
createdb dealcommerce
psql -d dealcommerce -f "01-estructura.sql"
psql -d dealcommerce -f "02-datos-demo.sql"
```

Con el proyecto levantado en Docker:

```bash
docker compose exec -T db psql -U dealcommerce -d dealcommerce < "01-estructura.sql"
docker compose exec -T db psql -U dealcommerce -d dealcommerce < "02-datos-demo.sql"
```

No hace falta correr `migrate` después: la tabla `django_migrations` viene incluida, así
que Django reconoce el esquema como al día.

## Qué datos no están

El repositorio es público y estos archivos se generaron para poder serlo. Se omitieron
las filas de estas tablas:

| Tabla | Motivo |
|---|---|
| `usuarios_usuario` | Hashes de contraseña de las cuentas de prueba |
| `agenda_visita` | Nombre, correo y teléfono de quien pidió una hora |
| `tiendas_solicituddeacceso` | Datos de contacto de quien escribió desde la portada |
| `agenda_enviocorreo` | Destinatarios de los correos de la agenda |
| `clientes_aprobacionmayorista` | Asocia un comprador con una tienda |
| `django_session` | Sesiones activas |
| `django_admin_log` | Actividad en el panel de administración |
| `ingesta_carga` | Registra quién subió cada planilla; apunta a `usuarios_usuario`, que no viene |
| `pedidos_pedido` | Las ventas reales del cliente piloto. Ver abajo |
| `pedidos_lineapedido` | Lo mismo: el detalle de esas ventas |

La estructura de todas esas tablas sí está en `01-estructura.sql`. Lo que se omitió son
las filas, no el modelo de datos.

El campo `token_feed` de `agenda_configuracionagenda` viene con un texto de relleno. Ese
token es la credencial del feed de calendario del dueño: quien lo tenga puede leer la
agenda de esa tienda sin iniciar sesión. Al restaurar conviene regenerarlo:

```python
from apps.agenda.models import ConfiguracionAgenda
ConfiguracionAgenda.objects.get(tienda__slug="joyas-ye").regenerar_token_feed()
```

## Sobre las cifras

**Los pedidos no vienen en este volcado, y es a propósito.** La base de la que se tomó
tiene el historial real de ventas de Joyas_ye: 2.795 ventas que el dueño llevó a mano
durante dos años. Los nombres de sus clientes están seudonimizados, pero los montos no:
son cuánto factura un negocio concreto, mes a mes, y eso no es nuestro para publicarlo en
un repositorio abierto.

Quien restaure estos archivos verá el catálogo y la tienda, y las pantallas de ventas,
pronóstico y segmentos dirán que no hay datos suficientes. Eso es correcto: sin ventas no
hay nada que medir ni que proyectar. Para reponerlas:

```bash
docker compose exec api python manage.py importar_historial "/datos/<planilla>.xlsx" --desplazar-anos 1
```

El archivo del cliente tampoco se versiona. Está en `data/` del proyecto, fuera del
repositorio. Cómo se lee, cómo se seudonimiza y por qué las fechas se adelantan un año
está en `EVIDENCIA DE SISTEMA APLICACION/docs/analitica.md`.

**Los precios del catálogo sí vienen**, porque son públicos: están en la vitrina de la
tienda, a la vista de cualquiera que entre.
