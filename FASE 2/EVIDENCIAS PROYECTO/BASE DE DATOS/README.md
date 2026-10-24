# Base de datos

PostgreSQL 17. El esquema se versiona con migraciones de Django; estos archivos son una
foto de la base para poder revisarla y restaurarla sin levantar el proyecto entero.

- `01-estructura.sql`: tablas, llaves foráneas, restricciones, índices y secuencias. Sin
  filas.
- `02-datos-demo.sql`: los datos de demostración. La tienda de ejemplo, su configuración
  de agenda y sus diez bloques de atención, más las tablas internas de Django.

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

Los montos y las ventas que muestra el panel son datos sintéticos generados por el
equipo, no ventas reales del cliente, y la aplicación los rotula como tales en pantalla.
