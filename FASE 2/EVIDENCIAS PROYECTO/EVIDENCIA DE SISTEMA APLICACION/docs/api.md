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
| `GET` | `/panel/cargas/limites` | dueño o vendedor |
| `GET` | `/panel/plantillas/<tipo>` | dueño o vendedor |
| `GET` | `/panel/cargas` | dueño o vendedor |
| `POST` | `/panel/cargas/<tipo>/validar` | dueño o vendedor |
| `POST` | `/panel/cargas/<id>/confirmar` | dueño o vendedor |
| `DELETE` | `/panel/cargas/<id>` | dueño o vendedor |

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

### Carga masiva

Tres pasos, y el orden importa: **validar, mirar, confirmar**. Validar no escribe una sola
fila del catálogo; lo que devuelve es lo que *pasaría*. El catálogo se toca recién al
confirmar, con el resumen ya a la vista. El archivo lo llenó una persona a mano, y entre
«subí la planilla» y «se cambiaron 180 precios» tiene que haber una pantalla donde mirar.

Hay tres tipos de carga: `productos`, `tramos` y `fotos`. El tipo viaja en la ruta.

| Paso | Petición | Qué hace |
|---|---|---|
| Qué se acepta | `GET /panel/cargas/limites` | extensiones y peso máximo |
| La plantilla | `GET /panel/plantillas/<tipo>` | `.xlsx` con los encabezados exactos |
| Validar | `POST /panel/cargas/<tipo>/validar` | revisa y **no escribe nada** |
| Confirmar | `POST /panel/cargas/<id>/confirmar` | aplica lo validado |
| Descartar | `DELETE /panel/cargas/<id>` | deja la carga como descartada |
| Historial | `GET /panel/cargas` | las últimas 50, con `?tipo=` |

`validar` devuelve **201** con un `cargaId`, y ese identificador es el que después se
confirma o se descarta. La carga queda guardada con el archivo original adentro, así que al
confirmar se **vuelve a leer el archivo** en vez de confiar en lo que manda el navegador:
entre los dos pasos pasa tiempo, y lo que se aplica tiene que ser lo que se revisó.

`DELETE` no borra la fila: la deja en estado `descartada`. El historial tiene que poder
mostrar también lo que se decidió no aplicar, que es información de auditoría igual que lo
aplicado. Confirmar o descartar algo ya resuelto responde 400.

Los límites no van escritos en el frontend: la pantalla los pregunta, para que el aviso de
«pesa demasiado» salga antes de subir y no después de esperar la subida completa.
`TAMANO_MAXIMO_CARGA` fija el peso máximo, 20 MB por omisión.

#### La plantilla de productos

Once columnas, en este orden. Solo tres son obligatorias; el resto puede venir vacío y toma
el valor por omisión que dice la tabla.

| Columna | Obligatoria | Qué acepta |
|---|---|---|
| `codigo` | sí | el código de la tienda. Es la clave: subir dos veces la misma planilla actualiza, no duplica |
| `nombre` | sí | texto |
| `descripcion` | no | texto |
| `categoria` | no | el **nombre** de una categoría que ya exista en la tienda |
| `forma_venta` | no | `unidad`, `lote` o `peso`. Por omisión `unidad` |
| `unidad_medida` | no | `unidad`, `g` o `kg`. Por omisión `g` si se vende por peso y `unidad` si no |
| `precio_neto` | sí | entero en pesos, sin IVA, mayor que 0 |
| `controla_stock` | no | sí o no. Por omisión sí |
| `stock` | no | número. Con control y celda vacía se entiende 0, no «sin dato» |
| `cantidad_minima` | no | número mayor que 0. Por omisión 1 |
| `foto` | no | el nombre del archivo dentro del `.zip` de fotos |

La categoría **no se crea sola**: tiene que existir antes en la tienda. Crearla desde la
planilla llenaría el catálogo de variantes mal escritas de la misma palabra.

#### La plantilla de tramos

Cuatro columnas, las cuatro obligatorias. La clave es (producto, unidad del umbral, umbral):
dos tramos con el mismo umbral y la misma unidad se pisarían, y el motor de precios no
sabría cuál aplicar.

| Columna | Qué acepta |
|---|---|
| `codigo_producto` | el código de un producto **que ya esté cargado** |
| `umbral` | desde cuánto aplica este precio. De 0 para arriba |
| `unidad_umbral` | `cantidad`, `monto` o `peso` |
| `precio_neto` | el precio unitario neto desde ese umbral. Entero mayor que 0 |

Un tramo **no es un descuento**: es el precio unitario neto a partir de ese volumen. No hay
porcentajes y no hay tramos de toda la tienda.

#### Cómo se leen las celdas

Lo que escribe la gente no coincide con lo que espera un programa, así que la lectura es
tolerante en la forma y estricta en el fondo:

- **Los encabezados se normalizan**: «Precio Neto», «precio neto» y «PRECIO_NETO» son la
  misma columna. Quien llena la planilla no tiene por qué adivinar cuál esperábamos.
- **Las listas cerradas aceptan el valor o su nombre visible**: en `forma_venta` pasan tanto
  `peso` como «Por peso», porque la plantilla muestra uno y la gente escribe el otro.
- **Los sí/no** aceptan `si`, `sí`, `s`, `true`, `verdadero`, `1`, `x` y sus contrarios. Una
  celda con cualquier otra cosa **falla** en vez de adivinar: acá adivinar cambia si el
  producto lleva inventario.
- **Una fila mala no bota a las demás.** Se anota con su número de fila *tal como se ve en
  Excel* —el encabezado cuenta como la 1— y su motivo, y el resto sigue.
- **Las columnas obligatorias se exigen antes de leer filas.** Sin eso, un archivo que no es
  la planilla se lee como cero filas y devuelve «0 nuevos, 0 rechazados», que se parece
  demasiado a que funcionó.

Cada fila pasa además por las validaciones cruzadas del modelo **antes** de prometer que se
puede aplicar. Si no se mirara acá, decir que algo se vende por peso pero se mide en
unidades aparecería recién al confirmar, con media planilla escrita.

Aplicar corre en una transacción: o entra la planilla entera o no entra nada. A medio
aplicar, el dueño no sabría qué quedó.

#### Lo que no está en la planilla

`cantidad_piezas` —cuántas piezas trae un lote— no viene en la plantilla y se completa desde
el panel. La composición del lote tampoco se carga por planilla.

#### Productos ausentes

El resumen de `productos` trae `ausentes`: los códigos que la tienda tiene y la planilla no
menciona. Confirmar con `desactivarAusentes: true` los **desactiva**, no los borra. Una
planilla incompleta no puede vaciar una tienda, y lo desactivado conserva su historial y sus
pedidos. Por omisión no se toca nada.

#### El .zip de fotos

Se emparejan por el **nombre del archivo sin extensión contra el código del producto**, que
es como quedan cuando se bajan del teléfono. El resumen dice cuántas se emparejaron, qué
productos quedaron sin foto y qué fotos no corresponden a ningún producto.

Un comprimido que sube un desconocido es de lo más peligroso que acepta un sistema, así que
acá se desconfía de todo:

- **Las rutas internas se ignoran.** De cada entrada se toma solo el nombre del archivo. Una
  entrada llamada `../../etc/passwd` es un intento de escribir fuera de donde corresponde.
- **El tamaño descomprimido tiene tope** —200 MB—, además del comprimido. Un `.zip` de dos
  megas puede descomprimirse en varios gigas y llenar el disco: eso tiene nombre propio,
  *zip bomb*.
- **Hay tope de cantidad de archivos** —500—, por lo mismo.
- **Cada imagen se valida por contenido**, no por su extensión: JPEG, PNG o WEBP hasta 3 MB.
- **El nombre con que se guarda lo pone el sistema.** El del archivo solo sirve para
  emparejar.

El tipo de archivo se determina **por su contenido y no por la extensión**, que la escribe
quien sube. Hay un caso que obliga a mirar dos veces: un `.xlsx` *es* un `.zip` por dentro y
tiene la misma firma, así que para distinguirlos hay que abrirlo y buscar
`xl/workbook.xml`. Sin eso, una planilla se aceptaría como si fueran fotos.

Se aceptan `.xlsx` y `.csv` para las planillas y `.zip` para las fotos. `.xls` y `.xlsm` se
rechazan con la instrucción de cómo convertirlos, en vez de un «formato no válido» a secas.

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

Con R2 hay un segundo detalle: un bucket nace **privado** y su endpoint S3 responde solo
a peticiones firmadas, así que la dirección que da el almacenamiento no la puede abrir un
navegador. Las fotos se publican por el dominio de `R2_PUBLIC_BASE_URL` —uno propio
conectado al bucket, o su subdominio `r2.dev`—. Subir sigue yendo por el endpoint con
las llaves; solo leer cambia de camino. Si falta esa variable con R2 configurado, Django **no
arranca**: vale más un error al partir que una vitrina de imágenes rotas en producción.

## Plataforma

| Método | Ruta | Quién |
|---|---|---|
| `POST` | `/solicitudes-de-acceso` | cualquiera, desde la portada |

Tiene su propio límite por IP (`THROTTLE_SOLICITUDES`). No responde nada que la persona no
haya escrito ella misma: un correo repetido devuelve un mensaje de recibo y no la
invitación a averiguar qué negocios ya pidieron entrar.

## Todavía sin endpoint

Las pantallas existen y su cliente de API tiene los tipos finales, pero el backend falta:
equipo, carrito, pedidos y todo lo de analítica. Mientras tanto esas pantallas dicen que
no están conectadas en vez de mostrar números inventados.
