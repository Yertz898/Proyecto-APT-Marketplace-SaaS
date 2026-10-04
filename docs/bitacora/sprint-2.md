# Sprint 2

## Qué se comprometió

Catálogo de lotes y granel, precios por tramos, carga masiva desde Excel y CSV, perfil de
la tienda, los pendientes del Sprint 1 en la interfaz y la documentación.

## Qué se cerró

**Catálogo y precios.** Las tablas del catálogo (`Categoria`, `Lote`, `ComposicionLote`,
`LineaGranel`) y las de precios (`TramoPrecio`, con umbrales en pesos, gramos o cantidad de
lotes). La regla del dinero quedó escrita una sola vez, en `apps/precios/dinero.py`.

**API pública del catálogo.** Los cuatro endpoints de `/t/<slug>/`: listado paginado de
lotes, detalle, listado de granel y detalle de línea. El listado no muestra lo agotado ni
lo inactivo.

**Datos de demostración.** `cargar_demo` deja el catálogo de Joyas_ye con los precios de
granel reales del cliente y seis lotes inventados que lo dicen en el nombre.

**Perfil de la tienda.** `GET` y `PATCH` de `/panel/tienda`, con la sección "Tienda y marca"
y vista previa de la vitrina antes de guardar. El plan decide en el backend qué campos se
pueden tocar.

**El panel completo como armazón.** Las quince secciones existen, agrupadas en una barra
lateral que dice en qué está cada una: candado si el plan no la incluye, punto si los datos
serían de ejemplo, "pronto" lo que no existe.

**Documentación.** `docs/api.md`, `docs/modelo-datos.md`, la tabla de endpoints del README
y esta bitácora.

## Qué quedó pendiente, y por qué

**Carga masiva (Fase 4).** Es lo único del compromiso que no se tocó. Leer `.xlsx` necesita
`openpyxl` y revisar un archivo por contenido necesita `filetype`; ninguna de las dos está
en `requirements/base.txt` y agregar dependencias no es una decisión que corresponda tomar
de paso. Además falta resolver el `.rar`: el frontend lo ofrece desde el Sprint 1 y
descomprimirlo en Python pide una biblioteca más, con binario del sistema. Las seis rutas y
sus tipos ya están acordados en `lib/api/panel.ts`.

**Catálogo y precios desde el panel.** Existen contra la vitrina pública, no contra el
panel: falta el CRUD. Las pantallas dicen que no están conectadas.

**Equipo.** Invitar a un vendedor manda un correo, y `EMAIL_BACKEND` no está configurado.

**Secciones en demostración.** Pedidos, ventas, pronóstico, segmentos, sugerencias y
asistente siguen sin su proveedor de ejemplo ni `NEXT_PUBLIC_MODO_DEMO`.

**Diccionario y diagrama.** `Tienda` ganó `plan` y `tipografia`; faltan en el `.xlsx` y en
el `.drawio`. Editar el Excel desde el código pide `openpyxl`, la misma dependencia que
está esperando aprobación.

## Decisiones que no venían en el prompt

- **Lista de tipografías**: Inter, Plus Jakarta Sans, Manrope y Cormorant Garamond. El
  prompt pedía una lista cerrada y no decía cuál.
- **La agenda sigue visible al público** aunque el panel la marque "Próximamente". Lo que
  está congelado es la bandeja del dueño, no lo que ya funciona.
- **En el plan Básico el perfil se puede abrir**, y lo que se bloquea son los campos. El
  documento pedía "solo el logo"; esconder la sección entera habría dejado al dueño sin
  poder cambiar ni el nombre de su tienda.
- **A un vendedor que intenta escribir se le responde 403 y no 404.** La regla del 404 es
  para datos de otra tienda; acá es su propia tienda y la ve igual.

## Diferencias con el diccionario de datos

El diccionario apareció en `docs/` con el trabajo ya empezado. Al revisarlo había seis
campos distintos, y se corrigió el código, no el diccionario:

| Campo | Estaba | Quedó |
|---|---|---|
| `Lote.material` | opcional | `varchar(60)` y obligatorio |
| `LineaGranel.material` | opcional | `varchar(60)` y obligatorio |
| `Lote.foto` | sin largo | `varchar(255)` |
| `LineaGranel.foto` | no existía | agregado |
| `LineaGranel.categorias` | relación muchos a muchos | `varchar(200)` de texto |
| `TramoPrecio.precio_unitario_neto` | — | se llama `valor` |

Las migraciones se regeneraron en vez de parchearse: nada estaba publicado todavía.

## Verificación

264 pruebas en el backend, **45 marcadas `aislamiento`**, cada una en los dos sentidos: que
A no ve lo de B y que B no ve lo de A. `ruff check` limpio, sin migraciones pendientes,
`tsc` y `eslint` limpios en el frontend.

```bash
docker compose exec api pytest -m aislamiento
```

## Anotado al pasar, sin tocar

- `apps/agenda/models.py` tiene el mismo patrón que causó un error real en el catálogo:
  Django descarta el `code` de un `ValidationError` cuando el mensaje es un diccionario. Ahí
  todavía no rompe nada porque ninguna prueba afirma sobre esos códigos.
- La portada promete un "mall online" genérico y el modelo del backend es de lotes y
  gramos, que es el negocio de Joyas_ye. Es una decisión de arquitectura, no un ajuste de
  texto, y hay que tomarla antes de sumar la segunda tienda.
- "Cómo funciona" y "Funciones" repiten lo mismo en la portada. Pide una reescritura, no un
  borrado.
