# Frontend

Next 16 con el App Router, React 19, TypeScript y Tailwind 4. Todo en `frontend/src`.

Dentro de un solo proyecto conviven **tres aplicaciones** que no comparten casi nada:

| Aplicación | Rutas | A quién le habla | Se ve |
|---|---|---|---|
| Portada de la plataforma | `/`, `/solicitar-acceso`, `/plataforma` | al dueño de una tienda que todavía no entra | claro, marca DealCommerce |
| Vitrina de la tienda | `/t/<slug>/…` | al comprador | como la tienda quiera; hoy, oscuro |
| Panel de la tienda | `/panel/…` | al dueño y a sus vendedores | claro, marca DealCommerce |

Están separadas a propósito. El panel **no comparte componentes con la vitrina** y nunca se
sirve bajo `/t/<slug>`: la tienda de quien trabaja en ella sale de su sesión, no de la
dirección. Si saliera de la dirección, cambiar el slug en la barra del navegador sería un
intento de entrar al panel de otra tienda, y eso no debería ser siquiera expresable.

## Dónde vive cada cosa

| Carpeta | Qué hay |
|---|---|
| `src/app/` | solo rutas: `page.tsx`, `layout.tsx` y su `metadata`. Casi nada de lógica |
| `src/components/portada/` | las secciones de la portada, una por archivo |
| `src/components/tienda/` | la vitrina: catálogo, ficha, carrito, agenda, encabezado y pie |
| `src/components/panel/` | el panel: barra lateral, guardia, pantallas y piezas compartidas |
| `src/components/plataforma/` | la administración de la plataforma |
| `src/components/sesion/` | formulario de entrada y registro, y el hook de sesión |
| `src/components/ui/` | componentes de shadcn sobre Base UI. Código prestado |
| `src/components/campo.tsx` | el campo de formulario de todo el proyecto |
| `src/lib/api/` | un módulo por área del backend. Nadie llama `fetch` fuera de acá |
| `src/lib/` | tipos, formato, sesión, rutas e identidad visual |

El alias `@/` apunta a `src/`.

## Lo que el frontend no hace

Esto vale la pena decirlo antes que cualquier otra cosa, porque explica la forma de media
aplicación: **acá no se protege nada y acá no se calcula ningún precio.**

- **Los guardias son cortesía.** `GuardiaDelPanel` y `GuardiaDePlataforma` evitan mostrar
  una pantalla que no va a funcionar. Quien decide es el backend, que exige token, rol y
  plan en cada endpoint. Un guardia de navegador se salta escribiendo la dirección o
  borrando un nodo del DOM, así que lo que hace el nuestro es **explicar, no esconder**:
  quien no tiene acceso ve por qué y qué puede hacer al respecto.
- **El candado del plan también.** Una sección bloqueada se marca, pero si alguien cambia su
  plan en `localStorage` no abre nada: el endpoint lo rechaza igual.
- **Ningún total se multiplica en el navegador.** El tramo que aplica depende del pedido
  completo y el stock puede agotarse mientras el comprador decide, así que cotizar es
  siempre trabajo del backend. El carrito guarda **solo códigos y cantidades**, nunca
  precios.
- **Las validaciones de formulario son para ahorrar un viaje.** El mensaje que se muestra lo
  redacta el backend, ya en español; el frontend no reescribe textos de error, solo los
  ubica junto al campo que corresponde.
- **Lo que revisa el navegador de un archivo que se sube** —extensión y tamaño— es para que
  el aviso salga antes de la espera. El backend valida por contenido.

## Las dos direcciones de la API

`src/lib/api/base.ts` exporta dos, y no es redundancia:

- `API_NAVEGADOR` (`NEXT_PUBLIC_API_URL`): por donde el navegador alcanza a Django, el
  puerto publicado en el host.
- `API_SERVIDOR` (`API_URL_INTERNO`): por donde lo alcanza el servidor de Next, que dentro
  de Docker es otro contenedor y llega por el nombre del servicio.

Usar la misma en los dos lados rompe uno. `API_URL_INTERNO` **no** lleva el prefijo
`NEXT_PUBLIC`: es una dirección de la red privada y no tiene por qué llegar al navegador.
Fuera de Docker no está definida y las dos terminan siendo la misma.

La regla práctica: un módulo que se llama desde un componente de servidor usa
`API_SERVIDOR`; uno que se llama desde el navegador —todo lo que pasa por `pedirConSesion`—
usa `API_NAVEGADOR`.

## Servidor o cliente

Por omisión, servidor. Se pasa a cliente solo cuando hace falta, y las razones son tres:

1. **Hay estado o eventos** (un formulario, un selector de cantidad, un menú).
2. **La petición necesita la sesión**, que vive en el navegador. En servidor saldría sin
   token y la respuesta llegaría vacía sin que nada fallara a gritos; por eso
   `PantallaCargas` es de cliente aunque solo muestre una tabla.
3. **La decisión depende del rol**, y eso es una función, que no cruza la frontera del
   servidor.

Cuando una pantalla tenía que ser de cliente pero necesitaba `metadata`, se parte en dos: la
página se queda de servidor con su `metadata` y el contenido se va a un componente de
cliente. Por eso hay pares como `app/panel/(con-sesion)/catalogo/page.tsx` y
`components/panel/pantalla-catalogo.tsx`.

El grupo `(con-sesion)` existe porque el formulario de entrada también vive bajo `/panel` y
no puede quedar detrás de la puerta que lleva hasta él.

## Sesión

`src/lib/sesion.ts` guarda los dos tokens y quién entró, y se lee con `useSyncExternalStore`
a través de `useSesion()`. No hay proveedor ni contexto: la sesión vive en un único almacén
de módulo y cualquier componente la lee de ahí.

`useSesion()` devuelve `{ sesion, hidratado }`, y **`hidratado` importa**. Antes de que el
navegador lea el almacenamiento, «sin sesión» no quiere decir que no haya: quiere decir que
todavía no se sabe. Un guardia que no distinga las dos cosas echa a la gente en cada carga.

`pedirConSesion` pone el token, y si venció lo renueva una vez y repite la llamada. Si el de
refresco tampoco sirve, borra la sesión: seguir con credenciales muertas solo produce
errores más adelante. Para un cuerpo `multipart` no escribe `Content-Type`, porque el
navegador tiene que agregar la frontera que separa las partes.

> **Pendiente de seguridad, anotado también en el código:** los tokens quedan en
> `localStorage`, así que un script inyectado en la página podría leerlos. Lo que de verdad
> los protege es una cookie `httpOnly`, y eso significa que el navegador deje de hablarle
> directo a Django y pase por el servidor de Next. Es una decisión de arquitectura que no
> está tomada. Mientras no se tome, la defensa es la de la sección siguiente: no renderizar
> nunca HTML ni CSS escrito por un vendedor.

## Las dos paletas

`src/app/globals.css` declara dos juegos de colores que conviven a propósito:

- **DealCommerce**, claro: `hueso`, `marino`, `pizarra`, `acero`, `ambar`, `arena`, `cielo`.
  Es la portada y el panel.
- **La vitrina**, oscuro: `tinta`, `superficie`, `violeta`, `lila`, `oro`, `texto`. Viene del
  mockup y es el tema por omisión de una tienda.

La portada le habla al vendedor y la tienda se ve como quiera: son marcas distintas y no
tienen por qué parecerse. Los tokens de shadcn apuntan a los colores de la vitrina para que
los componentes de la librería calcen con el diseño.

`campo.tsx` sirve a las dos caras con un `tema` de `"claro" | "oscuro"`: comparten la forma
—etiqueta, ayuda, error asociado por `aria`— y no los colores. No es de shadcn, y por eso no
vive en `components/ui`.

## Identidad de la tienda

Cada tienda elige cuatro colores. Entran al diseño por `variablesDeIdentidad()`, que los
convierte en variables CSS para aplicar con `style`, y **solo si son hexadecimales de seis
dígitos**; uno mal formado se ignora y queda el de la plataforma.

Nunca se inserta CSS ni HTML escrito por un vendedor. Todas las tiendas comparten origen: un
script inyectado en una podría leer la sesión de los compradores de otra.

Por lo mismo, los enlaces a redes pasan por `EnlaceExterno`, que **solo acepta `https://`**.
Hoy el valor lo escribe una persona y mañana lo entregará la API; un `javascript:` no debe
poder llegar nunca a un `href`.

Y `rutaSegura()` filtra el parámetro `volver` del inicio de sesión: tiene que empezar con una
sola barra. `//otro-sitio.cl`, `https://…` y `/\otro` son direcciones absolutas aunque
parezcan rutas, y dejarlas pasar convertiría el formulario en un trampolín para llevar a
alguien a una copia de la tienda justo después de escribir su contraseña.

## El panel

### Las secciones son datos

`components/panel/secciones.tsx` tiene las **catorce** secciones en una sola lista, con su
grupo, su plan mínimo, qué puede hacer un vendedor y en qué estado está. Están ahí como
datos porque tres cosas distintas las leen: la barra lateral para dibujarlas, el guardia
para decidir si se entra, y cada pantalla para saber si sus datos son reales.

`seccionDe(ruta)` resuelve la sección activa **de la más específica a la menos**. Comparado
al revés, `/panel` calza con todo y «Inicio» quedaría siempre marcado.

`planAlcanza()` compara contra una escalera `basico < premium < ultimate`, y `rolAlcanza()`
responde si el rol puede siquiera ver la sección: el dueño siempre puede, un vendedor según
el campo `vendedor` de cada una.

### Las piezas compartidas

`components/panel/piezas.tsx` junta lo que repite cada pantalla: `Cabecera`, `Tarjeta`,
`Cargando`, `Vacio`, `Error`, `SinPermiso`, `BloqueadaPorPlan`, `Proximamente` y
`SinConectar`. Están juntas para que las catorce pantallas se vean como una sola aplicación
y no como catorce: si cambia el espaciado de un encabezado, cambia en todas a la vez.

### Catálogo

`pantalla-catalogo.tsx` lista, filtra y abre el formulario; `formulario-producto.tsx` crea y
edita. Es **el mismo formulario para las tres formas de venta**, porque son el mismo
producto: lo que cambia es qué campos tienen sentido. Elegir «por peso» reemplaza las
unidades por gramos o kilos, elegir «por lote» habilita las piezas, y lo que no aplica no se
muestra a medias: no se muestra.

El listado del panel no es el de la vitrina. Acá aparece lo desactivado y lo agotado, que es
justamente lo que pide atención, y cada producto llega con **todo lo editable** y no con un
resumen: si faltara la descripción, el formulario la abriría vacía y guardar la borraría.

### Carga masiva

`/panel/cargas` es un índice con una tarjeta por tipo más el historial, y
`/panel/cargas/[tipo]` es la misma pantalla para los tres tipos. Agregar un tipo es agregar
una entrada en `lib/cargas.ts`, no escribir otra pantalla.

El recorrido es **validar, mirar, confirmar**: `carga-masiva.tsx` sube el archivo,
`resumen-carga.tsx` muestra qué pasaría, y recién el botón de confirmar escribe. Todos los
valores que vienen del archivo se muestran **como texto**, nunca interpretados como HTML: el
contenido lo escribió una persona fuera del sistema.

`lib/cargas.ts` además rechaza `.xls` y `.xlsm` **con la instrucción de cómo convertirlos**,
en vez de un «formato no válido» a secas. El formato de las plantillas está en
[`api.md`](api.md).

## La vitrina

El catálogo es **uno** —`/t/<slug>/productos`— con filtro por forma de venta. Antes eran dos
secciones fijas, `/lotes` y `/granel`, que describían a una tienda en particular; las
pestañas salen ahora de `formas-de-venta`, así que una tienda que solo vende por unidad no
ve ninguna.

Un solo componente por cosa, para las tres formas de venta:

| Componente | Qué dibuja |
|---|---|
| `tarjeta-producto.tsx` | el producto en la grilla |
| `ficha-producto.tsx` | la ficha con el selector de cantidad, en la unidad del producto |
| `disponibilidad.tsx` | la insignia de existencias, o nada si la tienda no lleva inventario |
| `tabla-tramos.tsx` | los tramos, en la unidad en que los definió la tienda |

Lo que cambia entre una forma de venta y otra no es el componente: son los datos. Un producto
por lote trae su composición, uno por peso trae tramos, y lo que no aplica no se dibuja.

El menú del encabezado es el mismo para toda tienda —inicio, catálogo, agenda— porque cómo
vende cada una es contenido de su catálogo y no una sección del sitio. Las categorías tampoco
van ahí: cambian entre tiendas.

`formatearCantidad(cantidad, unidad)` es el único lugar que escribe una unidad. La unidad
viene del producto: la plataforma no sabe si lo que se cuenta son gramos, piezas o lotes, y
no debe saberlo.

## Fechas y horas

En `lib/formato.ts`, y con dos reglas que no son evidentes:

- **Las horas se muestran siempre en hora de Chile**, con la zona fijada. Un comprador que
  viaja no debe ver su visita a otra hora que la tienda.
- **Las fechas `aaaa-mm-dd` son días del calendario, no instantes**, y se formatean y se
  suman en UTC. Interpretarlas en hora de Chile las correría al día anterior, porque
  `new Date("2026-09-28")` es medianoche UTC.

## `components/ui`: código prestado

Son componentes de shadcn sobre Base UI, traídos con su CLI. Están en inglés, con sus
convenciones y su formato, y **se dejan como vienen**: reescribirlos al español perdería la
posibilidad de actualizarlos. Todo lo nuestro va en las otras carpetas, en español, con la
convención del proyecto.

## Verificación

```bash
docker compose exec web npm run lint
```

```bash
docker compose exec web npx tsc --noEmit
```

```bash
docker compose exec web npm run build
```

Los tipos de ruta (`LayoutProps<"/t/[slug]">`, `PageProps<"/panel/cargas/[tipo]">`) los
genera Next, y `npm run build` los regenera.

En desarrollo, `next.config.ts` deja `images.unoptimized`: el optimizador corre dentro del
contenedor y Next se niega a optimizar imágenes de direcciones IP privadas, que es
exactamente lo que es la API vista desde ahí.

**No hay pruebas automatizadas de frontend.** No hay Vitest, Jest ni Playwright: lo que
respalda esta parte es el tipado, el linter, que el build pase y la revisión en el navegador.
Las pruebas del proyecto son todas del backend. Decirlo acá es parte de la deuda: las reglas
que importan —aislamiento, precios, permisos— viven en el backend y están cubiertas ahí, pero
una pantalla puede romperse sin que ninguna prueba lo note.

Un aviso que cuesta caro olvidar: el contenedor de `web` guarda `.next` en un volumen
anónimo, así que un archivo nuevo puede no aparecer hasta

```bash
docker compose up -d --force-recreate --renew-anon-volumes web
```

## Lo que hoy está desalineado

Anotado acá porque es más útil escrito que descubierto dos sprints después:

- **El campo `estado` de `secciones.tsx` no coincide con las pantallas.** Dice
  `demostracion` en Pedidos, Panel de ventas, Pronóstico, Segmentos y Asistente, y `real` en
  Precios y Equipo; las siete muestran `SinConectar`. La definición del tipo describe
  `demostracion` como «pantalla terminada con datos de ejemplo», y eso no existe todavía.
- **`FranjaDeDemostracion` y `AvisoSimulado`** quedaron sin uso cuando esas pantallas
  pasaron a `SinConectar`.
- **Precios tiene backend y no tiene pantalla.** Los endpoints de tramos existen y están
  documentados; la sección sigue en `SinConectar`.
- **El comentario de cabecera de `vista-carrito.tsx`** sigue hablando de lotes y granel como
  si fueran dos cosas del sistema, que es el lenguaje de antes del modelo `Producto`. El
  carrito todavía no está conectado, así que se corrige cuando se conecte.
