# Sprint 2

## Qué se comprometió

Catálogo y precios por tramos, carga masiva desde Excel y CSV, perfil de la tienda, los
pendientes del Sprint 1 en la interfaz y la documentación. El compromiso estaba escrito
sobre lotes y granel; a mitad del sprint pasó a ser sobre productos, por lo que explica la
sección «El cambio de modelo».

## Qué se cerró

**Catálogo y precios.** `Categoria`, `Producto` y `ComposicionLote`, más `TramoPrecio` con
umbrales en cantidad, monto o peso. La forma de vender es un dato del producto, no una
tabla por rubro. El motor de precios vive en `apps/precios/servicios.py` y la regla del
dinero, una sola vez, en `apps/precios/dinero.py`.

**API pública.** `/t/<slug>/productos` con filtro por forma y por categoría, el detalle,
`formas-de-venta` —con lo que la vitrina arma sus pestañas desde los datos— y `cotizar`. El
listado no muestra lo agotado ni lo inactivo.

**Catálogo en el panel.** Listado con lo que la vitrina esconde, inventario en cuatro
cifras, y crear y editar productos con su foto. Cierra H2-EP02.

**Datos de demostración.** `cargar_demo` carga dos tiendas: Joyas_ye, con los precios
reales del cliente y seis lotes inventados que lo dicen en el nombre, y Bazar Austral,
inventada entera, que vende por unidad y lleva inventario.

**Perfil de la tienda.** `GET` y `PATCH` de `/panel/tienda`, con la sección "Tienda y marca"
y vista previa de la vitrina antes de guardar. El plan decide en el backend qué campos se
pueden tocar.

**El panel completo como armazón.** Las catorce secciones existen, agrupadas en una barra
lateral que dice en qué está cada una: candado si el plan no la incluye, punto si los datos
serían de ejemplo, "pronto" lo que no existe.

**Documentación.** `docs/api.md`, `docs/modelo-datos.md`, la tabla de endpoints del README
y esta bitácora.

## El cambio de modelo, a mitad del sprint

Con el sprint empezado apareció `Cambios_Programacion` (versión 2) y corrigió un error de
enfoque que veníamos arrastrando: el dominio estaba hecho a la medida de Joyas_ye.
`CONVENCIONES.md` decía textualmente «no hay productos, ni variantes, ni stock por pieza» y
el código lo siguió al pie de la letra, con una tabla `Lote` y otra `LineaGranel`, y una
vitrina con dos secciones fijas.

Eso describe a un cliente, no a un centro comercial. DealCommerce arrienda locales a
cualquier PYME del retail: una tienda de ropa vende prendas una por una y lleva inventario,
otra vende por kilo, Joyas_ye vende lotes cerrados y gramos. Las tres tienen que caber sin
inventar tablas por cliente.

**Qué se hizo.** `Lote` y `LineaGranel` se funden en **`Producto`**, con `forma_venta`
(`unidad`, `lote`, `peso`) e inventario opcional. Los cupos dejan de ser un concepto: son
el stock de un producto vendido por lote, y uno que se vende una sola vez tiene stock 1.
Los tramos de precio pasan a colgar siempre de un producto. Lo de Joyas_ye queda como la
configuración de **una** tienda, en su propia sección de `CONVENCIONES.md`.

**Se hizo ahora porque después no se podía.** Las migraciones del catálogo no estaban
publicadas y los únicos datos los generaba `cargar_demo`. Con pedidos encima, esto habría
sido una migración de datos.

## Decisiones que no estaban en el prompt

- **Las migraciones 0001 de `catalogo` y `precios` se rehicieron** en vez de escribir una
  migración de transformación. Nada fuera de esas dos apps dependía de ellas y los únicos
  datos eran los de demostración. Aprobado antes de hacerlo.
- **El endpoint de cotización adelanta trabajo del Sprint 3.** El motor de precios es de
  allá, pero la vitrina ya lo necesitaba para mostrar un precio por volumen, así que se
  construyó el servicio completo y se expuso `POST /t/<slug>/productos/<codigo>/cotizar`.
- **No hay `DELETE` de productos.** El catálogo se desactiva, no se borra: un producto
  borrado se lleva por delante su composición, sus tramos y las líneas de pedido que lo
  nombren.
- **Los descuentos salen del alcance.** Un tramo es un precio unitario neto por volumen,
  nunca un porcentaje, y no existen tramos de toda la tienda. Con eso se fue también la
  sección «Sugerencias» del panel, que queda en catorce.
- **Una segunda tienda de demostración**, Bazar Austral, inventada entera, que vende por
  unidad y lleva inventario. Con una sola tienda el aislamiento no se ve a mano.
- **`.rar` fuera de la carga de fotos.** Leerlo en el servidor pedía el binario `unrar`,
  que es propietario y Debian deja en non-free; en un repositorio público no corresponde.
  Windows comprime en `.zip` de fábrica, así que nadie queda afuera.

### De antes del cambio de modelo

- **Lista de tipografías**: Inter, Plus Jakarta Sans, Manrope y Cormorant Garamond. El
  prompt pedía una lista cerrada y no decía cuál.
- **La agenda sigue visible al público** aunque el panel la marque "Próximamente". Lo que
  está congelado es la bandeja del dueño, no lo que ya funciona.
- **En el plan Básico el perfil se puede abrir**, y lo que se bloquea son los campos. El
  documento pedía "solo el logo"; esconder la sección entera habría dejado al dueño sin
  poder cambiar ni el nombre de su tienda.
- **A un vendedor que intenta escribir se le responde 403 y no 404.** La regla del 404 es
  para datos de otra tienda; acá es su propia tienda y la ve igual.

## Dos errores que encontraron las pruebas

Vale la pena dejarlos escritos porque los dos habrían pasado una revisión a ojo:

- **Un tramo duplicado no se detectaba** y el error de integridad llegaba a PostgreSQL, que
  responde 500 sin decir qué repetir.
- **Sobrescribir `get_queryset` en el detalle de un tramo dejó fuera el filtro por tienda**,
  así que se podía borrar el tramo de otra. Lo cazó una prueba marcada `aislamiento`. El
  queryset ahora se declara como atributo y lo acota el mixin.

## Qué quedó pendiente, y por qué

**Carga masiva.** Es lo único del compromiso que no se tocó. Leer `.xlsx` necesita
`openpyxl` y revisar un archivo por contenido necesita `filetype`; ninguna de las dos está
en `requirements/base.txt` y agregar dependencias no es una decisión que corresponda tomar
de paso. Además falta resolver el `.rar`: el frontend lo ofrece desde el Sprint 1 y
descomprimirlo en Python pide una biblioteca más, con binario del sistema. Las seis rutas y
sus tipos ya están acordados en `lib/api/panel.ts`.

**El carrito y los pedidos.** El contrato existe y la cotización ya está hecha; falta
`Pedido`, `LineaPedido` y el descuento de stock con bloqueo de fila.

**Equipo.** Invitar a un vendedor manda un correo, y `EMAIL_BACKEND` no está configurado.

**Secciones en demostración.** Pedidos, ventas, pronóstico, segmentos, sugerencias y
asistente siguen sin su proveedor de ejemplo ni `NEXT_PUBLIC_MODO_DEMO`.

**Diccionario y diagrama.** Los corrige Pedro, con el modelo nuevo.

## Diferencias con el diccionario de datos

El diccionario apareció en `docs/` con el trabajo ya empezado, y se corrigió el código para
calzar con él en seis campos de `Lote` y `LineaGranel`. Ese trabajo quedó superado por el
cambio de modelo: esas dos tablas ya no existen.

**El diccionario y el diagrama los corrige Pedro**, con `Producto` y sus campos nuevos
—`forma_venta`, `controla_stock`, `stock`, `unidad_medida`, `cantidad_minima`—, el
`TramoPrecio` sin tramos de tienda, y `Tienda.plan` y `Tienda.tipografia`, que siguen
faltando desde antes.

## Verificación

400 pruebas en el backend, **59 marcadas `aislamiento`**, cada una en los dos sentidos: que
A no ve lo de B y que B no ve lo de A. `ruff check` limpio, sin migraciones pendientes,
`tsc` y `eslint` limpios en el frontend.

```bash
docker compose exec api pytest -m aislamiento
```

## Anotado al pasar, sin tocar

- `apps/agenda/models.py` tiene el mismo patrón que causó un error real en el catálogo:
  Django descarta el `code` de un `ValidationError` cuando el mensaje es un diccionario. Ahí
  todavía no rompe nada porque ninguna prueba afirma sobre esos códigos.
- "Cómo funciona" y "Funciones" repiten lo mismo en la portada. Pide una reescritura, no un
  borrado.
