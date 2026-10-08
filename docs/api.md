# API

Todo cuelga de `/api`. Las respuestas van en camelCase porque el frontend las consume
directamente; las tablas de la base usan los nombres del diccionario de datos.

DealCommerce es un centro comercial en línea: cada tienda tiene su vitrina pública y su
panel. Lo que vende cada una y cómo lo vende son datos suyos, no ramas del código. Por eso
hay un solo endpoint de productos y no uno por rubro.

## Cómo se resuelve la tienda

Hay dos formas y solo dos:

- **Vitrina pública** — la tienda va en la ruta, `/api/t/<slug>/…`. Es lo que ve cualquiera
  sin sesión. Un slug que no existe, o una tienda inactiva, responde **404** sin distinguir
  entre las dos cosas: decir cuál es cuál confirmaría qué slugs existen.
- **Panel** — la tienda **sale del token** y de ninguna otra parte. Por eso esas rutas no la
  nombran: no existe la petición que pida los datos de otra tienda.

Un `tienda_id` en el cuerpo o en la query string no se confía nunca. Lo mismo vale para el
asistente conversacional cuando exista: lo que pida queda acotado a la tienda del token.

## Errores

Siempre la misma forma, con el mensaje ya redactado en español:

```json
{"error": {"codigo": "validacion",
           "mensaje": "Revisa los datos marcados.",
           "detalles": {"email": ["Ya hay una cuenta con este correo."]}}}
```

`detalles` es siempre `{campo: [mensajes]}`, aunque el mensaje sea uno solo. Un fallo de
autenticación y un bloqueo por frecuencia responden siempre el mismo texto: distinguirlos
diría si el correo existe.

| Código HTTP | Cuándo |
|---|---|
| 400 | Datos inválidos. El detalle dice qué campo. |
| 401 | Sin sesión, o con un token vencido. |
| 403 | Con sesión, pero el rol no alcanza. |
| 404 | No existe **o es de otra tienda**. Nunca 403 por esto. |
| 405 | El método no aplica. Un producto no se borra: se desactiva. |
| 429 | Demasiados intentos. |

## Sesión y cuentas

| Método | Ruta | Quién | Devuelve |
|---|---|---|---|
| `POST` | `/auth/sesion` | cualquiera | `access`, `refresh`, `usuario` |
| `POST` | `/auth/sesion/renovar` | cualquiera | `access` |
| `POST` | `/auth/registro` | cualquiera | crea un **comprador** y lo deja con sesión |
| `GET` | `/auth/yo` | con sesión | el `usuario` de la sesión |

`usuario` trae `email`, `nombre`, `rol`, `rolNombre` y `tienda`. `tienda` es `null` para un
comprador o un administrador de plataforma, y `{slug, nombre, plan}` para quien trabaja en
una. El `plan` viaja ahí porque el panel decide con él qué secciones ofrece; quien decide
de verdad es el backend en cada endpoint.

El rol nunca se manda en el registro: lo fija el backend. Mandarlo no sirve de nada.

Las tres rutas de sesión comparten un límite de intentos por IP (`THROTTLE_AUTENTICACION`).

## Vitrina pública

Sin sesión. La tienda sale del slug de la ruta.

| Método | Ruta | Devuelve |
|---|---|---|
| `GET` | `/t/<slug>/tienda` | identidad: `slug`, `nombre`, `logo`, `banner`, `colores`, `redes` |
| `GET` | `/t/<slug>/formas-de-venta` | cómo vende **esta** tienda |
| `GET` | `/t/<slug>/productos` | `{productos, paginaActual, totalPaginas}`, 12 por página |
| `GET` | `/t/<slug>/productos/<codigo>` | un producto |
| `POST` | `/t/<slug>/productos/<codigo>/cotizar` | qué cuesta una cantidad |
| `GET` | `/t/<slug>/agenda/horas` | horas disponibles; filtra con `desde` y `hasta` |
| `POST` | `/t/<slug>/agenda/visitas` | pide una hora (**comprador con sesión**) |

`colores` es `null` cuando la tienda no definió los cuatro: con la paleta a medias, la
vitrina usa la de la plataforma en vez de mezclar.

**`formas-de-venta` es lo que hace innecesaria una lista escrita en el frontend.** Devuelve
solo las que esa tienda usa de verdad, así que una que vende únicamente por unidad no
muestra pestañas, y otra que mañana agregue venta por peso la muestra sin tocar código.

El listado acepta `?forma=` y `?categoria=`. Una forma que no existe devuelve vacío y no
400: viene de la URL, y un enlace viejo no debería reventar la vitrina.

### Un producto

```json
{"codigo": "BAZ-01", "nombre": "Taza de cerámica", "descripcion": "Cerámica esmaltada.",
 "categoria": "cocina", "formaVenta": "unidad", "unidadMedida": "unidad",
 "precioNeto": 4990, "iva": 948, "precioTotal": 5938,
 "disponibilidad": {"tipo": "disponible", "restantes": 120}, "agotado": false,
 "cantidadMinima": 1, "piezasTotales": null, "composicion": [],
 "tramos": [{"umbral": 12, "unidadUmbral": "cantidad", "precioNeto": 4490}],
 "minimo": null, "foto": null}
```

Es **un solo tipo para las tres formas de venta**: lo que no aplica viaja en `null` o
vacío, nunca en otra forma. Así el frontend tiene un tipo y no tres.

`disponibilidad` distingue cuatro situaciones que el frontend no debería tener que deducir:
`sin_control` (la tienda no lleva inventario de esto), `agotado`, `ultima` (queda una) y
`disponible` con cuántas. La última unidad va aparte porque empuja a decidir.

Los precios van **netos**; el IVA se calcula aparte y viaja al lado, nunca sumado por
dentro. El listado público **no** incluye lo agotado ni lo inactivo.

### Cotizar

```json
{"cantidad": 900, "precioUnitario": 560, "neto": 504000, "iva": 95760, "total": 599760,
 "tramoAplicado": 500, "unidadTramo": "peso",
 "aviso": "Llevando 1000 g pagas $500.000 neto, menos que ahora.",
 "rechazo": null, "motivo": null}
```

**Un rechazo responde 200, no 400.** La petición está bien hecha; la respuesta es «no se
puede, por esto», y la vitrina necesita mostrar la razón donde corresponde en vez de una
pantalla de error. `motivo` distingue los tres casos: `bajo_minimo_por_monto`,
`bajo_cantidad_minima` y `sin_stock`.

El `aviso` aparece cuando llevar más sale más barato que lo pedido. Se avisa y no se cambia
la cantidad por el comprador: la decisión es suya.

## Panel de la tienda

Con sesión. La tienda sale del token. Entran el dueño y los vendedores, salvo donde se diga.

| Método | Ruta | Quién |
|---|---|---|
| `GET` | `/panel/tienda` | dueño o vendedor |
| `PATCH` | `/panel/tienda` | **solo el dueño** |
| `GET` `POST` | `/panel/productos` | dueño o vendedor |
| `GET` `PATCH` | `/panel/productos/<codigo>` | dueño o vendedor |
| `GET` `POST` | `/panel/productos/<codigo>/tramos` | dueño o vendedor |
| `GET` `PATCH` `DELETE` | `/panel/tramos/<id>` | dueño o vendedor |
| `GET` `POST` | `/panel/categorias` | dueño o vendedor |
| `GET` `PATCH` `DELETE` | `/panel/categorias/<id>` | dueño o vendedor |
| `GET` | `/panel/inventario` | dueño o vendedor |

### Catálogo

El listado del panel **no** es el de la vitrina: acá aparece lo desactivado y lo agotado,
que es justamente lo que pide atención, y el orden lo pone adelante. Cada producto trae un
`estado` en una palabra —`publicado`, `ultima`, `agotado`, `desactivado`— y **todo lo
editable**, no un resumen: si faltara la descripción, el formulario la abriría vacía y
guardarla la borraría.

**No hay `DELETE` de productos, y es deliberado.** Acá el catálogo no se borra, se
desactiva. Un producto borrado se lleva por delante su composición, sus tramos y las líneas
de pedido que lo nombren. Intentarlo responde 405.

El `PATCH` y el `POST` aceptan **multipart**, porque la foto es un archivo. La categoría se
asigna **por nombre** y no por identificador: el nombre es único dentro de la tienda, y un
id en el cuerpo sería una invitación a probar los de otra.

Las reglas cruzadas del producto se validan antes de tocar la base y responden 400 con el
campo marcado. Sin eso, decir que algo se vende por peso pero se mide en unidades llegaría
hasta PostgreSQL y volvería como un 500 que no dice qué arreglar.

### Inventario

Cuatro cifras: publicados, con una sola unidad, agotados y desactivados. Son **hechos**. La
alerta por demanda proyectada que piden los documentos necesita el pronóstico, que todavía
no existe, y un número sin respaldo en una pantalla de inventario es peor que no tenerlo.

### Perfil de la tienda

`slug` y `plan` son de solo lectura: el primero es la dirección pública que la tienda ya
repartió, el segundo lo administra la plataforma.

- Los colores se validan como hexadecimal de seis dígitos. Todas las tiendas comparten
  origen: un valor arbitrario sería CSS de una corriendo en la página de otra.
- Las imágenes se revisan **por contenido**, no por la extensión del nombre, que la escribe
  quien sube el archivo. Se aceptan JPEG, PNG y WEBP hasta 3 MB. SVG no: es XML que puede
  traer scripts.
- En el plan Básico solo pasan `nombre` y `logo`. El resto se rechaza con el código
  `requiere_plan`, aunque llegue sin pasar por la pantalla.

A un vendedor que intenta escribir se le responde **403 y no 404**: es su propia tienda y
la ve igual, no se le está escondiendo nada.

### Dónde viven las imágenes

La dirección de una imagen **no depende de quién la pide**. Sale de la configuración: en
producción la entrega Cloudflare R2 ya absoluta, y en desarrollo se le antepone
`MEDIA_BASE_URL`. Antes se armaba con el host de la petición, y entonces la misma foto
llegaba como `localhost:8000` al navegador y como `api:8000` al servidor de Next, que
ningún navegador resuelve.

## Plataforma

| Método | Ruta | Quién |
|---|---|---|
| `POST` | `/solicitudes-de-acceso` | cualquiera, desde la portada |

Tiene su propio límite por IP (`THROTTLE_SOLICITUDES`). No responde nada que la persona no
haya escrito ella misma: un correo repetido devuelve un mensaje de recibo y no la
invitación a averiguar qué negocios ya pidieron entrar.

## Todavía sin endpoint

Las pantallas existen y su cliente de API tiene los tipos finales, pero el backend falta:
carga masiva (`/panel/cargas/…`), equipo, carrito, pedidos y todo lo de analítica. Mientras
tanto esas pantallas dicen que no están conectadas en vez de mostrar números inventados.
