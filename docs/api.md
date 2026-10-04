# API

Todo cuelga de `/api`. Las respuestas van en camelCase porque el frontend las consume
directamente; las tablas de la base usan los nombres del diccionario de datos.

## Cómo se resuelve la tienda

Hay dos formas y solo dos:

- **Vitrina pública** — la tienda va en la ruta, `/api/t/<slug>/…`. Es lo que ve cualquiera
  sin sesión. Un slug que no existe, o una tienda inactiva, responde **404** sin distinguir
  entre las dos cosas: decir cuál es cuál confirmaría qué slugs existen.
- **Panel** — la tienda **sale del token** y de ninguna otra parte. Por eso esas rutas no
  la nombran: no existe la petición que pida los datos de otra tienda.

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
| `GET` | `/t/<slug>/lotes` | `{lotes, paginaActual, totalPaginas}`, 12 por página |
| `GET` | `/t/<slug>/lotes/<codigo>` | un lote |
| `GET` | `/t/<slug>/granel` | las líneas de granel con sus tramos |
| `GET` | `/t/<slug>/granel/<codigo>` | una línea |
| `GET` | `/t/<slug>/agenda/horas` | horas disponibles; filtra con `desde` y `hasta` |
| `POST` | `/t/<slug>/agenda/visitas` | pide una hora (**comprador con sesión**) |

`colores` es `null` cuando la tienda no definió los cuatro: con la paleta a medias, la
vitrina usa la de la plataforma en vez de mezclar.

Un lote:

```json
{"tipo": "lote", "codigo": "DEMO-01", "nombre": "Surtido de aros (ejemplo)",
 "material": "Enchape de plata", "piezasTotales": 18,
 "composicion": [{"categoria": "aros", "cantidad": 12}],
 "precioNeto": 45990, "iva": 8738, "precioTotal": 54728,
 "cupos": {"tipo": "MULTIPLE", "restantes": 8}, "agotado": false, "foto": null}
```

`cupos` es una unión: `{"tipo": "UNICO"}` para la pieza que se vende una sola vez, y
`{"tipo": "MULTIPLE", "restantes": n}` cuando hay varios. Los precios van **netos**; el IVA
se calcula aparte y viaja al lado, nunca sumado por dentro.

Una línea de granel trae sus `tramos` ordenados —primero los umbrales en pesos, después los
en gramos— y un `minimo` ya redactado por el backend. El listado público **no** incluye los
lotes agotados ni los inactivos.

## Panel de la tienda

Con sesión. La tienda sale del token.

| Método | Ruta | Quién |
|---|---|---|
| `GET` | `/panel/tienda` | dueño o vendedor |
| `PATCH` | `/panel/tienda` | **solo el dueño** |

El `GET` devuelve el perfil más dos cosas que el panel necesita y no son del modelo:
`tipografiasDisponibles`, la lista cerrada de fuentes, y `puedeEditarLaMarca`, que dice si
el plan de la tienda abre algo más que el nombre y el logo.

El `PATCH` va **multipart**, porque el logo y el banner son archivos. Acepta solo lo que
cambió. Y:

- `slug` y `plan` son de solo lectura. El primero es la dirección pública que la tienda ya
  repartió; el segundo lo administra la plataforma.
- Los colores se validan como hexadecimal de seis dígitos. Todas las tiendas comparten
  origen: un valor arbitrario en un color sería CSS de una corriendo en la página de otra.
- Las imágenes se revisan **por contenido**, no por la extensión del nombre, que la escribe
  quien sube el archivo. Se aceptan JPEG, PNG y WEBP hasta 3 MB. SVG no: es XML que puede
  traer scripts.
- En el plan Básico solo pasan `nombre` y `logo`. El resto se rechaza con el código
  `requiere_plan`, aunque llegue sin pasar por la pantalla.

A un vendedor que intenta escribir se le responde **403 y no 404**: es su propia tienda y
la ve igual, no se le está escondiendo nada.

## Plataforma

| Método | Ruta | Quién |
|---|---|---|
| `POST` | `/solicitudes-de-acceso` | cualquiera, desde la portada |

Tiene su propio límite por IP (`THROTTLE_SOLICITUDES`). No responde nada que la persona no
haya escrito ella misma: un correo repetido devuelve un mensaje de recibo y no la
invitación a averiguar qué negocios ya pidieron entrar.

## Todavía sin endpoint

Las pantallas existen y su cliente de API tiene los tipos finales, pero el backend falta:
carga masiva (`/panel/cargas/…`), catálogo y precios desde el panel, equipo, pedidos y todo
lo de analítica. Mientras tanto esas pantallas dicen que no están conectadas en vez de
mostrar números inventados.
