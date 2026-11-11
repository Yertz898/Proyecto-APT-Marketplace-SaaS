# Sprint 3

## Qué se comprometió

Las cuatro tarjetas del tablero: motor de precios por tramos, carrito y pedido, panel de
ventas del vendedor y datos para los modelos.

## Qué se cerró

**Carrito y pedido.** Cotización en vivo del carrito completo y confirmación con descuento
de inventario. El pedido guarda una copia de los precios del momento, así que lo cobrado no
cambia aunque después cambie el catálogo. El pago no pasa por la plataforma: se devuelve el
folio y un enlace de WhatsApp con el detalle.

**Bandeja de pedidos.** El dueño ve qué le pidieron, con quién hablar y qué se cobró, y
mueve el estado. Los estados avanzan y no retroceden; anular devuelve el inventario con la
fila bloqueada.

**Panel de ventas.** Ventas del mes contra el anterior, lo que falta coordinar, los cinco
productos que más dejaron en noventa días y los que llevan ese tiempo sin venderse.

**Datos para los modelos.** El historial real del cliente leído, seudonimizado e importado:
2.795 ventas en quince meses. Con eso el Sprint 4 tiene con qué trabajar.

**Documentación.** `docs/ventas-y-pedidos.md` con los estados del pedido y cada indicador,
el origen de los datos y sus límites en `docs/analitica.md`, y los endpoints nuevos en
`docs/api.md`.

## El carrito cobraba treinta por ciento de más

Es el hallazgo del sprint y conviene dejarlo escrito entero.

El carrito calculaba los precios por su cuenta en vez de usar `apps/precios/servicios.py`.
Llamaba a `producto.calcular_precio_tramo(...)` dentro de un `hasattr`, y ese método **no
existe en el proyecto**: la condición siempre daba falso, el `hasattr` se tragaba el error
y caía al precio base. Lo mismo con `obtener_aviso_conveniencia` y con `cupos_disponibles`.

Medido: mil gramos de la línea hombre, que el cliente cobra a $500 el gramo por tramo, se
cobraban a $650. La ficha del producto mostraba el precio correcto en la pantalla anterior.

Las historias H1-EP06 y H2-EP06 —tramos y aviso de conveniencia— figuraban como construidas
y el comprador nunca las vio. No lo detectó nadie porque `pedidos` no tenía una sola prueba
y porque un lote simple, que es con lo que se prueba a mano, no tiene tramos.

Otras tres del mismo módulo, encontradas al escribir las pruebas:

- **El checkout ignoraba el formulario.** Tomaba el nombre de `request.user` usando
  `username`, atributo que nuestro modelo de usuario no tiene, y un invitado quedaba
  guardado como «Cliente Vitrina / Por coordinar», sin forma de contactarlo. El formulario
  de contacto en la vitrina es nuevo de este sprint.
- **El enlace de WhatsApp iba a un número inventado.** Leía `tienda.telefono_contacto`, que
  no existe —el campo se llama `whatsapp`— y caía a un `56900000000` escrito a mano.
- **El carrito podía pedir productos desactivados**, porque buscaba sobre todo el catálogo
  y no sobre lo publicado.

Las cuatro tienen la misma forma: **un `hasattr` o un `getattr` con valor por omisión
tapando un atributo que no existe**. El código no falla, responde otra cosa.

## El historial del cliente

Joyas_ye no lleva registro digital de sus ventas. Lo único que existe es una planilla que
el dueño llevó a mano durante dos años, y **su formato cambió siete veces** siguiendo al
negocio: primero vendía piezas sueltas, después lotes y hoy vende por gramo. Cada versión
dejó su propio bloque de columnas al lado del anterior, en la misma hoja.

Lo que se decidió, con el detalle en `docs/analitica.md`:

- **Los nombres se seudonimizan.** Son 1.821 personas que no dieron permiso para aparecer
  en un repositorio público, y el volcado de la base sí viaja a las evidencias.
- **El mapeo de tramos de costo a productos sale de los datos**, no de una suposición: los
  precios por gramo que de verdad se cobraron son los de los tres productos por gramo que
  la tienda tiene publicados.
- **Las fechas se adelantan un año entero**, en años y no en meses, para que cada venta
  conserve su mes y la estacionalidad no se corra.

## Decisiones que no estaban en el prompt

- **El código se movió a la carpeta de evidencias.** Había dos copias del mismo proyecto,
  una en la raíz del repositorio y otra dentro de `FASE 2/EVIDENCIAS PROYECTO/`. La que
  revisa la comisión es la segunda, así que esa es la única que queda. De las 304 rutas,
  294 eran idénticas y las 10 restantes eran trabajo sin confirmar que nunca había llegado
  a la copia que se evalúa.
- **`docker-compose.yml` fija el nombre del proyecto.** Compose lo deducía del nombre de la
  carpeta contenedora: al mover el código habría creado volúmenes nuevos y la base habría
  aparecido vacía sin que nada lo avisara.
- **`Pedido` tenía cuatro columnas de fecha para dos conceptos**, las heredadas de
  `ModeloDeTienda` y dos propias. Cualquier consulta podía tomar la equivocada sin fallar.
  Quedan las heredadas.
- **Un pedido pendiente no cuenta como venta** en los indicadores. El pago se coordina
  fuera de la plataforma, así que entre confirmar y transferir puede no pasar nada;
  contarlo infla el mes con plata que no llegó. Va aparte, como lo que falta coordinar.
- **«Sin movimiento» deja fuera lo publicado dentro de la ventana.** Un lote que entró al
  catálogo la semana pasada no está detenido: nunca tuvo tiempo, y marcarlo empujaría al
  dueño a rebajar algo que todavía no se ofreció.
- **La columna `foto` de la carga masiva ahora sirve para algo.** La plantilla y la
  pantalla decían que el nombre del archivo salía de esa columna, y nadie la leía: el
  emparejado era contra el código del producto y nada más. Quien subía sus fotos con el
  nombre que ya tenían veía «carga exitosa» y cero fotos emparejadas. Está en el historial
  de cargas que pasó de verdad.
- **Una tienda sin WhatsApp no recibe enlace.** Es mejor que uno que no lleva a nadie: con
  el enlace roto, el comprador cree que avisó.

## Qué quedó pendiente, y por qué

**La agenda del dueño sigue congelada**, esperando que el cliente confirme si la agenda
sigue en el alcance. El lado público funciona y no se tocó.

**La invitación de vendedores (TEC-04) no se hizo.** Aparece en el Sprint Backlog y no en
el tablero, que es el documento que el equipo mantiene al día. Los roles existen desde el
Sprint 1; falta la pantalla y configurar el envío de correo, que la plataforma todavía no
hace.

**Pruebas de frontend: sigue sin haber ninguna.** Lo que respalda esa parte es el tipado,
el linter y la revisión a mano.

**El `granel.json` que nombra la checklist del tablero no existe.** Sus casos sí, como
pruebas en `apps/precios/tests/test_servicios.py` con los precios reales del cliente.

## Verificación

588 pruebas en el backend al cierre, entre ellas las 27 de `pedidos` que no existían —con
el aislamiento en los dos sentidos, que era tarea explícita del sprint— y las 18 de los
indicadores. `ruff check` limpio, sin migraciones pendientes, `tsc` y `eslint` limpios.

Probado también a mano contra la vitrina: agregar al carrito, llenar el formulario,
confirmar, y ver el pedido en la bandeja del panel con su cambio de estado.
