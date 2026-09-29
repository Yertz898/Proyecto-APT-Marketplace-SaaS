# Base de datos — DealCommerce

PostgreSQL 17. El esquema se versiona con migraciones de Django; estos archivos
son una foto de esa base para poder revisarla y restaurarla sin levantar el
proyecto entero.

## Archivos

| Archivo | Qué trae |
|---|---|
| `01-estructura.sql` | Todas las tablas, llaves foráneas, restricciones `CHECK`, índices y secuencias. Sin una sola fila. |
| `02-datos-demo.sql` | Los datos de demostración: la tienda de ejemplo, su configuración de agenda y sus diez bloques de atención. Más las tablas internas de Django que hacen falta para que la base quede consistente. |

## Cómo restaurarla

```bash
createdb dealcommerce
psql -d dealcommerce -f "01-estructura.sql"
psql -d dealcommerce -f "02-datos-demo.sql"
```

Con Docker, estando el proyecto levantado:

```bash
docker compose exec -T db psql -U dealcommerce -d dealcommerce < "01-estructura.sql"
docker compose exec -T db psql -U dealcommerce -d dealcommerce < "02-datos-demo.sql"
```

Después de restaurar no hace falta correr `migrate`: la tabla
`django_migrations` viene incluida, así que Django reconoce el esquema como al
día.

## Qué se dejó fuera, y por qué

Este repositorio es público. Estos archivos se generaron para poder serlo, y
eso significó sacar cosas a propósito:

| Tabla | Motivo |
|---|---|
| `usuarios_usuario` | Guarda los hashes de contraseña de las cuentas de prueba. Un hash publicado se puede atacar sin límite de intentos y fuera de la vista de nadie. |
| `agenda_visita` | Nombre, correo y teléfono de quien pidió una hora. |
| `tiendas_solicituddeacceso` | Lo mismo: datos de contacto de quien escribió desde la portada. |
| `agenda_enviocorreo` | Destinatarios de los correos de la agenda. |
| `clientes_aprobacionmayorista` | Asocia a un comprador con una tienda. |
| `django_session` | Sesiones activas. |
| `django_admin_log` | Quién tocó qué en el panel de administración. |

La **estructura** de todas esas tablas sí está en `01-estructura.sql`: lo que se
omitió son las filas, no el modelo de datos.

Además, el campo `token_feed` de `agenda_configuracionagenda` viene reemplazado
por el texto `REEMPLAZAR-AL-RESTAURAR-token-de-ejemplo`. Ese token es la
credencial del feed de calendario del dueño: quien lo tenga puede leer la agenda
de esa tienda sin iniciar sesión. Al restaurar conviene regenerarlo:

```python
from apps.agenda.models import ConfiguracionAgenda
ConfiguracionAgenda.objects.get(tienda__slug="joyas-ye").regenerar_token_feed()
```

## Nota sobre las cifras

Los montos y las ventas que aparecen en la interfaz del panel son **datos
sintéticos generados por el equipo**, no ventas reales del cliente, y la
aplicación los rotula como tales en pantalla.
