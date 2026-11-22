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
asistente conversacional: lo que pida queda acotado a la tienda del token.

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
| `POST` | `/t/<slug>/carrito/cotizar` | qué cuesta el carrito completo; no escribe nada |
| `POST` | `/t/<slug>/pedidos` | cierra el pedido y devuelve folio y enlace de WhatsApp |
| `POST` | `/t/<slug>/agenda/visitas` | pide una hora (**comprador con sesión**) |
| `GET` | `/t/<slug>/agenda/mis-visitas` | «Mis citas»: las visitas del comprador en la tienda, con el cambio pendiente (**comprador**) |
| `POST` | `/t/<slug>/agenda/mis-visitas/<id>/cambio` | el cliente propone otra hora `{inicio}` (**comprador**) |
| `POST` | `/t/<slug>/agenda/mis-visitas/<id>/cambio/respuesta` | responde la hora que propuso la tienda `{acepta}`; rechazar cancela la visita (**comprador**) |
| `POST` | `/t/<slug>/agenda/mis-visitas/<id>/cancelar` | cancela la visita (**comprador**) |
| `GET`, `POST` | `/agenda/cambios/enlace` | ver y responder un cambio con la firma del enlace del correo (sin sesión; vence en 7 días) |

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
| `GET` | `/panel/pedidos/` | dueño o vendedor |
| `PATCH` | `/panel/pedidos/<id>/estado/` | dueño o vendedor |
| `GET` | `/panel/ventas` | dueño o vendedor |
| `GET` | `/panel/pronostico` | dueño o vendedor |
| `GET` | `/panel/segmentos` | dueño o vendedor |
| `GET` `POST` | `/panel/asistente` | dueño o vendedor |

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

Cuatro cifras: publicados, con una sola unidad, agotados y desactivados. Son **hechos**, y
por eso esta respuesta no trae la alerta por demanda proyectada: esa es una estimación y
vive en `/panel/pronostico`, como `diasHastaQuiebre` de cada producto. Mezclarlas haría
que el dueño no supiera cuál de los números se midió y cuál se calculó.

### Ventas, pronóstico y segmentos

Las tres respuestas alimentan pantallas con gráficos, y por eso traen **la serie completa**
y no solo los totales. Qué significa cada indicador está en `ventas-y-pedidos.md` y
`analitica.md`; acá va la forma.

**`GET /panel/ventas`** trae, además de las cifras del mes, `serieMensual`: los últimos
**doce meses** de pedidos confirmados y entregados, uno por fila.

```jsonc
"serieMensual": [
  { "mes": "2025-12", "etiqueta": "dic 25", "pedidos": 323, "total": 14422468, "enCurso": false },
  // …
  { "mes": "2026-11", "etiqueta": "nov 26", "pedidos": 0, "total": 0, "enCurso": true }
]
```

- **Los meses sin ventas vienen igual, en cero.** Si se omitieran, el gráfico uniría octubre
  con diciembre como si fueran seguidos y una caída se vería como una línea plana.
- **El mes en curso viene marcado con `enCurso`.** Va por la mitad, así que siempre suma
  menos que un mes cerrado; la pantalla lo dibuja punteado para que no parezca un desplome.

**`GET /panel/pronostico`** trae por producto su `serie` mensual de cantidades, la
proyección, el `metodo` con que se calculó —`null` cuando no hay historial suficiente— y
`diasHastaQuiebre`, que es `null` sin pronóstico o en productos que no controlan stock.

**`GET /panel/segmentos`** trae el conteo de cada grupo, el umbral de días con que se
decidió y la lista de clientes. La lista son **los doce que más gastaron de cada grupo**, en
el orden de prioridad general, y no los cincuenta primeros: ordenados por prioridad, los
cincuenta salían todos «en riesgo» y el dueño no tenía cómo mirar a sus habituales. El
conteo sí es del total; la lista es para saber a quién escribirle, no para recorrer la base.

### Asistente

`GET /panel/asistente` lista las preguntas que sabe contestar y el largo máximo.
`POST /panel/asistente` recibe `{"pregunta": "..."}` y responde:

```jsonc
{
  "intencion": "pronostico",
  "texto": "Para el próximo mes espero …",
  "seccion": "pronostico",       // a qué pantalla del panel ir por el detalle
  "clasificadoPor": "modelo"     // o "palabras clave"
}
```

`clasificadoPor` dice quién entendió la pregunta: Gemini, cuando hay `GEMINI_API_KEY` y
respondió, o la tabla de palabras clave. En las ocho preguntas conocidas el `texto` lo arma
el backend. Una pregunta que no es ninguna de ellas vuelve con `"intencion":
"consulta_libre"`: Gemini la redacta con la ficha de la tienda (`apps/asistente/ficha.py`),
conteos y montos que arma el backend con el filtro de tienda, sin datos de clientes. Sin
modelo, o si falla, queda `"no_entendi"`. Detalle en `analitica.md`.

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

### Cuenta, equipo, plan y agenda

| Método | Ruta | Quién | Qué hace |
|---|---|---|---|
| `PATCH` | `/auth/yo` | cualquiera con sesión | cambia el nombre propio |
| `POST` | `/auth/contrasena` | cualquiera con sesión | cambia la contraseña; pide la actual |
| `POST` | `/auth/contrasena/olvido` | público | `{email, tienda?}`: manda el enlace por correo; responde lo mismo exista o no la cuenta |
| `POST` | `/auth/contrasena/restablecer` | público | `{uid, token, password}`: contraseña nueva con el enlace (vence en 1 hora, sirve una vez) |
| `GET`, `POST` | `/panel/equipo` | dueño, plan Premium | lista el equipo y crea vendedores |
| `PATCH` | `/panel/equipo/<id>` | dueño, plan Premium | renombra o desactiva a un vendedor |
| `POST` | `/panel/equipo/<id>/contrasena` | dueño, plan Premium | le pone otra contraseña a un vendedor |
| `GET`, `PATCH` | `/panel/plan` | dueño | ve y cambia el plan |
| `POST` | `/panel/plan/cancelar` | dueño | cancela: la vitrina se cierra, los datos quedan |
| `POST` | `/panel/plan/reanudar` | dueño | reabre una suscripción cancelada |
| `GET`, `PATCH` | `/panel/agenda/configuracion` | dueño o vendedor, Premium | reglas de la agenda |
| `GET`, `POST` | `/panel/agenda/bloques` | ídem | tramos de atención; rechaza los que se cruzan |
| `PATCH`, `DELETE` | `/panel/agenda/bloques/<id>` | ídem | un tramo |
| `GET`, `POST` | `/panel/agenda/dias-cerrados` | ídem | feriados y días sin atención |
| `DELETE` | `/panel/agenda/dias-cerrados/<id>` | ídem | reabre un día |
| `GET` | `/panel/agenda/visitas` | ídem | visitas desde hoy (`?todas=1` para todas) |
| `POST` | `/panel/agenda/visitas/<id>/estado` | ídem | confirmar, rechazar, asistió, no asistió |
| `POST` | `/panel/agenda/visitas/<id>/cambio` | ídem | la tienda propone otra hora `{inicio}` |
| `POST` | `/panel/agenda/visitas/<id>/cambio/respuesta` | ídem | responde la hora que propuso el cliente `{acepta}`; rechazar cancela la visita |

Reagendar: propone una parte y responde la otra. Aceptar mueve la visita (si estaba confirmada, busca cupo en la hora nueva); rechazar la cancela. Cada paso registra un aviso en `EnvioCorreo`, que solo sale por correo con `CORREOS_AGENDA_ACTIVOS=True` (apagado mientras no haya dominio verificado en Resend; lo pendiente se manda con `manage.py enviar_correos_agenda`).

El plan se revisa en el backend (`PlanMinimo` en `apps/core/permissions.py`); el candado del
panel solo lo refleja. No hay cobro en línea: cada cambio de plan queda en el registro de
actividad, que es lo que la administración usa para facturar.

La carga masiva suma el tipo `ventas` (`/panel/cargas/ventas/validar`): ventas anteriores a
la plataforma, que entran como pedidos entregados con su fecha real, sin tocar el
inventario y sin duplicarse si se sube el mismo archivo dos veces.

## Plataforma

| Método | Ruta | Quién |
|---|---|---|
| `POST` | `/solicitudes-de-acceso` | cualquiera, desde la portada |
| `GET`, `POST` | `/plataforma/tiendas` | administrador: todas las tiendas, y alta de tienda con su dueño |
| `GET`, `PATCH` | `/plataforma/tiendas/<slug>` | administrador: nombre, plan, plantilla y si está abierta |
| `GET` | `/plataforma/solicitudes` | administrador |
| `PATCH` | `/plataforma/solicitudes/<id>` | administrador: estado y notas |
| `GET` | `/plataforma/registros` | administrador: registro de actividad, con `?tienda=`, `?accion=`, `?q=` y `?pagina=` |

Al crear una tienda se puede mandar `solicitud` con el id de la solicitud de acceso de la
que sale: en la misma transacción esa solicitud queda como activada. La pantalla lo hace
con el botón «Crear tienda desde esta solicitud», que además llena el formulario.

**Cerrar no es borrar.** No hay endpoint para eliminar una tienda. Cerrarla (`activa:
false`) la saca de la vitrina y conserva todo. Si la cerró su dueño al cancelar el plan,
el dueño entra normalmente, para poder reanudarlo. Si la cerró la administración
(`Tienda.cerrada_por_la_plataforma`):

- **Los vendedores no inician sesión.** Reciben el código `tienda_cerrada` y el aviso de
  que el dueño puede escribirle a DealCommerce.
- **El dueño sí inicia sesión**, y la sesión trae `tienda.cerrada: true`. El panel se le
  reduce a una pantalla, **Escribir a DealCommerce**, y cada endpoint del panel lo sigue
  rechazando. Su mensaje va a `POST /panel/mensaje-a-la-plataforma` con su sesión y solo
  el texto: la tienda, el nombre y el correo los pone el backend desde la cuenta.
- La administración lo lee en `GET /plataforma/mensajes` y lo marca con
  `PATCH /plataforma/mensajes/<id>` (`leido`).
- Al abrir el panel se vuelve a pedir `/auth/yo`, así que cuando la tienda se reabre el
  dueño recupera el panel sin volver a iniciar sesión.

`/solicitudes-de-acceso` tiene su propio límite por IP (`THROTTLE_SOLICITUDES`). No
responde nada que la persona no haya escrito ella misma: un correo repetido devuelve un
mensaje de recibo y no la invitación a averiguar qué negocios ya pidieron entrar.

### Registro de actividad

`apps/auditoria` anota sola cada alta, cambio y baja hecha desde la API en las apps de la
tienda (catálogo, precios, pedidos, agenda, tiendas, usuarios, cargas), campo por campo, con
quién, cuándo y desde qué IP. También los inicios de sesión de dueños, vendedores y
administradores, los cambios de plan y de contraseña. Nunca guarda contraseñas. Lo que corre
por comando (datos de demostración, migraciones) no se anota.

## Vitrina pública: portada y compra

- `GET /t/<slug>/destacados` devuelve `masVendidos` (últimos 90 días, sin pedidos anulados)
  y `nuevos`. Sin ventas, `masVendidos` viene vacío y la portada no dibuja ese carrusel.
- `GET /t/<slug>/tienda` incluye `plantilla`: `clasica`, `moderna` o `minimal`.
- `POST /t/<slug>/pedidos` sin sesión exige `rut_contacto` válido y `email_contacto`: es la
  compra como visitante. Con sesión no se piden.

## Carrito, pedidos y ventas

El recorrido completo, los estados y de dónde sale cada indicador están en
`ventas-y-pedidos.md`. Lo que importa saber acá:

- **Cotizar no escribe nada** y se puede repetir en cada cambio de cantidad. Los precios
  salen del mismo motor que la ficha del producto, así que los tramos y el aviso de
  conveniencia llegan al carrito.
- **Confirmar vuelve a cotizar** en el servidor y no confía en lo que manda el navegador.
  Si alguna línea ya no se puede pedir, responde `400` y no crea nada.
- `nombre_contacto` y `telefono_contacto` son **obligatorios**, también para un comprador
  con sesión: el pago se coordina fuera de la plataforma y un pedido sin forma de
  contactar a quien lo hizo no se puede cerrar.
- En el panel, **la tienda sale del token** y no de la URL. Un pedido de otra tienda
  responde `404` y no `403`: que exista ya es información que no corresponde.

```jsonc
// POST /t/joyas-ye/pedidos
{
  "nombre_contacto": "Camila Rojas",
  "telefono_contacto": "+56 9 8765 4321",
  "direccion_entrega": "",          // opcional
  "notas": "",                      // opcional
  "lineas": [{ "codigo": "LOTE-039", "cantidad": 2 }]
}
```

```jsonc
// 201
{
  "numero": "DC-2FCE5FC5",
  "mensaje": "Tu pedido quedó registrado con el folio DC-2FCE5FC5…",
  "enlaceWhatsapp": null            // null si la tienda no tiene WhatsApp configurado
}
```
