# Modelo de datos

El diagrama entidad-relación está en [`DealCommerce_Modelo_ER.drawio`](DealCommerce_Modelo_ER.drawio)
y el diccionario completo, campo por campo, en
[`DealCommerce_Diccionario_de_Datos.xlsx`](DealCommerce_Diccionario_de_Datos.xlsx). Este
documento no los repite: explica por qué las tablas quedaron así.

## El punto de partida

DealCommerce es un centro comercial en línea. Cada tienda arrienda su local, sube sus
productos y los vende **a su manera**: una de ropa vende prendas una por una y lleva
inventario; una verdulería vende por kilo; una joyería arma conjuntos cerrados y además
vende por gramo. El sistema no sabe de ninguno de esos rubros, y no debe saberlo.

Lo que la plataforma sí provee es un lugar donde esa forma de vender se **declara como
dato**:

- `forma_venta` dice si el producto se vende por unidad, por lote o por peso.
- `controla_stock` dice si esa tienda lleva inventario de ese producto.

Nada de eso está escrito en el código. Una tienda que mañana venda de otra manera se
configura, no se programa.

> **Joyas_ye** es el cliente piloto y es **una tienda del centro comercial**, no el modelo
> del sistema. Vende por lote y por gramo; otra tienda vende por unidad. Cuando este
> documento nombra lotes o gramos es para explicar cómo quedó configurada ella, nunca
> porque la plataforma trate de eso.

## La regla que ordena todo

**Todo dato del sistema cuelga de una tienda.** Un modelo que no puede responder a qué
tienda pertenece está mal modelado. Por eso casi todas las tablas heredan de
`ModeloDeTienda`, que aporta la llave foránea a `Tienda` y un manager cuyo queryset ya
viene acotado.

La única excepción es `SolicitudDeAcceso`, y no es un descuido: es exactamente lo que
existe *antes* de que haya una tienda.

El aislamiento no se escribe de nuevo en cada app. Vive en `backend/apps/core/` y el resto
lo usa. Toda funcionalidad que lea datos de tienda lleva su prueba marcada
`@pytest.mark.aislamiento`, y esas pruebas corren con **dos** tiendas con datos: una prueba
con una sola tienda no puede detectar una fuga.

```bash
docker compose exec api pytest -m aislamiento
```

## Tienda

`Tienda` es la raíz. Guarda el `slug` —que es su dirección pública, `/t/<slug>/`— y su
identidad visual: logo, banner, cuatro colores en hexadecimal y una tipografía.

Dos decisiones que se ven en el esquema:

- **La tipografía es una lista cerrada** (`inter`, `jakarta`, `manrope`, `cormorant`), no un
  texto libre. Todas las tiendas comparten origen: una fuente o un CSS escritos por un
  arrendatario correrían en la página de otro. Por la misma razón los colores se validan
  con una expresión regular de seis dígitos hexadecimales.
- **El `plan`** (`basico`, `premium`, `ultimate`) decide qué secciones del panel se
  habilitan. Vive en la tienda y no en el usuario porque se suscribe el local, no la
  persona.

## Producto

Una sola tabla para todo lo que se vende en el centro comercial.

| Campo | Para qué |
|---|---|
| `codigo` | Como lo llama la tienda. Único **por tienda**, y es la clave de la carga masiva |
| `forma_venta` | `unidad`, `lote` o `peso` |
| `unidad_medida` | `unidad`, `g` o `kg`, según la forma de venta |
| `controla_stock` | Si esa tienda lleva inventario de este producto |
| `stock` | Cuánto queda (`Decimal`), **nulo** si no se controla |
| `cantidad_minima` | Lo menos que se puede pedir |
| `cantidad_piezas` | Solo en la venta por lote: contra esto cuadra la composición |

El código es único por tienda y no en toda la plataforma: dos locales pueden tener su
`A-01` sin saber uno del otro.

**El stock nulo no es cero.** Nulo significa «esta tienda no cuenta lo que le queda de este
producto»; cero significa «se acabó». Confundirlos haría desaparecer de la vitrina lo que
en realidad está disponible, y una restricción de la base impide la combinación imposible:
con control, el stock existe y no es negativo; sin control, es nulo.

Las otras restricciones están en la base y no en el código, para que no dependan de que
alguien las recuerde: la unidad tiene que corresponder a la forma de venta, las piezas solo
existen en la venta por lote, y el precio y la cantidad mínima son positivos.

### Lo que se vende por lote

Un lote es un conjunto cerrado que se compra entero. `ComposicionLote` dice cuántas piezas
de cada categoría trae, y la suma tiene que cuadrar con `cantidad_piezas`: es una validación
al guardar, no un comentario. No es una lista de piezas concretas —los modelos varían según
lo que le llega a la tienda—, así que lo que se promete es la mezcla.

**Los «cupos» no son un concepto aparte**: son el stock de un producto vendido por lote, y
uno que se vende una sola vez es un producto con `stock = 1`. Así descontar inventario es
una sola lógica para todo el centro comercial, en vez de dos que hay que recordar mantener
iguales.

### Categorías

Las define cada tienda, no la plataforma. Las usan el catálogo, la composición de los lotes
y el pronóstico de demanda. Son únicas por tienda, así que dos locales pueden tener una
«cocina» cada uno sin pisarse.

## Precios por volumen

`TramoPrecio` dice «desde tal cantidad, este precio por unidad de medida». **Siempre cuelga
de un producto y su valor es siempre un precio neto**: en DealCommerce no hay descuentos ni
porcentajes. Si hace falta otro precio, es otro tramo.

El umbral se mide en `cantidad`, `monto` o `peso`, y es **inclusivo**: «sobre 20 mil»
incluye los $20.000 exactos. Lo confirmó el cliente el 27-09-2026.

Cómo se elige el tramo, en `apps/precios/servicios.py`:

1. Los umbrales en `peso` o en `cantidad` tienen prioridad: se toma el mayor que la
   cantidad pedida alcance.
2. Si no alcanza ninguno, se arma un **monto de referencia** —la cantidad por el
   `precio_neto` del producto— y se aplica el tramo por `monto` que ese monto alcance.
3. Si no llega ni al primero, se rechaza.
4. Sin tramos, se cobra el precio del producto.

**Hay dos rechazos y no son lo mismo.** No alcanzar el primer tramo por monto es una cosa;
pedir menos que la `cantidad_minima` del producto es otra. Tienen mensajes distintos porque
se corrigen de maneras distintas.

Tres reglas del dinero, en `apps/precios/dinero.py`:

- Los precios se guardan **netos**, como enteros. El IVA (19%) se calcula aparte y se
  muestra separado del neto y del total. Nunca va sumado por dentro.
- El neto trunca hacia abajo y el IVA redondea con `ROUND_HALF_UP`, con `Decimal`. El
  `round()` de Python redondea al par más cercano y deja el total un peso corto en casos
  como 3.828,50.
- Las cantidades se guardan como `Decimal`, nunca como `Float`: una venta por peso admite
  decimales y de ahí sale un precio.

## Agenda

`ConfiguracionAgenda` por tienda y `BloqueHorario` por franja de atención. Cada bloque
hereda de la configuración lo que no define, para que una tienda pueda personalizar uno sin
repetir todo. Las horas se calculan, no se guardan: la disponibilidad sale del bloque menos
las visitas ya tomadas.

Todo se muestra en la hora de Santiago, sin importar dónde esté el navegador. Quien viaja ve
la hora de la tienda, no la de su teléfono.

El módulo está **congelado**: funciona el lado público, falta la bandeja del dueño.

## Datos de demostración

```bash
docker compose exec api python manage.py cargar_demo
```

Carga **dos tiendas**, y son dos a propósito: con una sola, el aislamiento no se ve a mano.

| Tienda | Cómo vende | Inventario |
|---|---|---|
| Joyas Ye | Por lote y por gramo | Los lotes sí; el gramo no |
| Bazar Austral | Por unidad | Sí, con tramos por cantidad |

Los tramos y los precios de Joyas_ye son **los que entregó el cliente, tal cual**: no se
corrigen ni se redondean. Sus seis lotes, en cambio, son inventados y lo dicen en el
nombre. Bazar Austral es inventada entera.

El comando es idempotente y **no repone el stock ya vendido** al volver a correrlo: hacerlo
borraría las ventas y la demostración mentiría.
