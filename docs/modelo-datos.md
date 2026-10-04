# Modelo de datos

El diagrama entidad-relación está en [`DealCommerce_Modelo_ER.drawio`](DealCommerce_Modelo_ER.drawio)
y el diccionario completo, campo por campo, en
[`DealCommerce_Diccionario_de_Datos.xlsx`](DealCommerce_Diccionario_de_Datos.xlsx). Este
documento no los repite: explica por qué las tablas quedaron así.

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
  vendedor correrían en la página de otra. Por la misma razón los colores se validan con
  una expresión regular de seis dígitos hexadecimales.
- **El `plan`** (`basico`, `premium`, `ultimate`) decide qué secciones del panel se
  habilitan. Vive en la tienda y no en el usuario porque se suscribe la tienda, no la
  persona.

Ambos campos se agregaron en el Sprint 2 y **faltan en el diccionario y en el diagrama**.

## Catálogo

Dos formas de vender, y por eso dos tablas y no una con un campo `tipo`:

| Tabla | Qué es |
|---|---|
| `Lote` | Un conjunto cerrado de piezas, con un precio por el conjunto |
| `ComposicionLote` | Cuántas piezas de cada categoría trae ese lote |
| `LineaGranel` | Una familia de piezas que se vende por gramo |
| `Categoria` | Anillos, aros, colgantes… Únicas **por tienda** |

Un lote se vende por **cupos**, no por stock de piezas. `tipo_cupo` distingue la pieza que
existe una sola vez (`UNICO`, y una restricción obliga a que sus cupos sean exactamente 1)
del lote que se arma varias veces (`MULTIPLE`). Las restricciones de base garantizan que
los cupos disponibles nunca superen los totales y que las piezas sean positivas: eso no
depende de que el código lo recuerde.

`LineaGranel.categorias` es **texto**, no una relación. Es lo que dice el diccionario y
tiene sentido: ahí la categoría es descriptiva —"colgantes, aros y anillos"— y no una
entidad que haya que contar ni filtrar.

El código de un lote es único por tienda, no global: dos tiendas pueden tener su `A-01` sin
saber una de la otra.

## Precios

`TramoPrecio` sirve a los dos casos, y por eso `linea_granel` puede ir vacío:

- **Con línea** es un tramo del granel de esa línea, y `valor` es el precio por gramo.
- **Sin línea** es un tramo por cantidad de lotes de toda la tienda.

Los tramos por cantidad de lotes **el cliente no los ha definido**, así que la tienda parte
sin ninguno. Quedan configurables por tienda y nunca escritos en el código.

Tres reglas del dinero que están en el esquema o en `apps/precios/dinero.py`:

- Los precios se guardan **netos**, como enteros. El IVA (19%) se calcula aparte y se
  muestra separado del neto y del total. Nunca va sumado por dentro.
- El cálculo usa `Decimal`: el neto trunca hacia abajo y el IVA redondea con `ROUND_HALF_UP`.
  El `round()` de Python redondea al par más cercano y deja el total un peso corto en casos
  como 3.828,50.
- Los umbrales son **inclusivos** (`>=`): "sobre 20 mil" incluye los $20.000 exactos. Lo
  confirmó el cliente el 27-09-2026.

En el granel los umbrales en gramos tienen prioridad. Si la cantidad no alcanza ninguno, se
arma un monto de referencia con el precio del primer tramo y se aplica el tramo en pesos
que ese monto alcance. Bajo $20.000 de referencia la compra se rechaza.

Los gramos se guardan como `Decimal`, nunca como `Float`.

## Agenda

`ConfiguracionAgenda` por tienda y `BloqueHorario` por franja de atención. Cada bloque
hereda de la configuración lo que no define, para que el vendedor pueda personalizar uno
sin repetir todo. Las horas se calculan, no se guardan: la disponibilidad sale del bloque
menos las visitas ya tomadas.

Todo se muestra en la hora de Santiago, sin importar dónde esté el navegador. Quien viaja
ve la hora de la tienda, no la de su teléfono.

El módulo está **congelado**: funciona el lado público, falta la bandeja del dueño.

## Datos de demostración

```bash
docker compose exec api python manage.py cargar_demo
```

Es idempotente: se puede correr las veces que haga falta. Deja a Joyas_ye en plan Ultimate
con su paleta, 7 categorías y 5 líneas de granel con **los precios reales que entregó el
cliente**, más 6 lotes `DEMO-01` a `DEMO-06` que son **inventados** y lo dicen en el
nombre. No repone los cupos ya vendidos al volver a correrlo.
