# DealCommerce

Marketplace SaaS multi-tienda con analítica predictiva para PYMES del retail.
Proyecto de título (Capstone PTY4614, Duoc UC). Equipo de dos personas, 18 semanas.

Cliente piloto real: **Joyas_ye**, joyería con tienda física y canal en redes sociales
que vende **solo por lotes cerrados y por gramo, a revendedores**. No vende piezas
sueltas ni lleva stock. El dueño es hombre; referirse a él como "el cliente" o "el dueño".

## El invariante que no se rompe

La aplicación aloja a **varios comercios sobre una misma base de datos**. Cada consulta
debe quedar acotada a la tienda del usuario autenticado. Una omisión acá no produce un
error visible: produce una filtración silenciosa de datos comerciales de terceros.

Reglas concretas:

- Ningún queryset del backend accede a datos sin filtrar por tienda. Si escribes un
  `Model.objects.all()` sobre una tabla con `tienda_id`, está mal.
- El filtro por tienda se aplica en una capa común (manager o mixin), no repetido a mano
  en cada vista, para que no se olvide en la siguiente.
- Toda funcionalidad nueva que lea datos de tienda lleva su prueba de aislamiento:
  autenticarse como tienda A e intentar leer datos de la tienda B debe responder
  `404`, nunca `403` (ver [Pruebas](#pruebas)).
- La tienda de cada petición sale del JWT, nunca del cuerpo ni de la URL (ver
  [Decisiones técnicas cerradas](#decisiones-técnicas-cerradas)).

## Stack

**Frontend** — React con Next.js, Tailwind CSS, shadcn/ui.
**Backend** — Django con Django REST Framework. Autenticación por JWT.
**Base de datos** — PostgreSQL. Migraciones versionadas de Django, nunca SQL suelto.
**Archivos** — Cloudflare R2 para imágenes de producto. La base guarda solo la referencia.
**Analítica** — Python: pandas, scikit-learn, XGBoost.
**Entorno** — Docker y docker-compose. Todo se levanta con un comando.

No introducir tecnologías nuevas sin que se pidan. El stack se eligió para reducir riesgo,
no por preferencia.

## Modelo de dominio

- **Tienda** — cada comercio suscrito. Es la raíz del aislamiento.
- **Lote** — unidad de venta cerrada, y la forma principal de vender. Campos: `codigo`
  (único por tienda), nombre, precio neto, `tipo_cupo` (`MULTIPLE` o `UNICO`),
  `cupos_totales`, `cupos_disponibles`, cantidad de piezas, material predominante y
  `activo`. Un lote de cupo único tiene un cupo: se vende una sola vez.
- **Composición del lote** — cuántas piezas trae de cada categoría (anillos, aros,
  cadenas…). La suma de la composición debe cuadrar con la cantidad de piezas del lote:
  es una validación al guardar, no un comentario. Un lote **no** es una lista de piezas
  concretas, porque los modelos varían según lo que le llega al cliente.
- **Línea de granel** — venta por gramo, con sus tramos de precio. No tiene stock: el
  cliente no registra gramos, así que lleva un interruptor de disponibilidad que el dueño
  enciende y apaga a mano.
- **Pedido** — checkout **simulado**: se genera el pedido y se descuentan cupos, pero no
  se cobra. El pago se coordina fuera de la plataforma.
- **Cliente comprador** — se le calculan variables de recencia, frecuencia y monto (RFM)
  para el modelo de segmentación.

No hay productos, ni variantes, ni stock por pieza. Si un modelo nuevo parece necesitar
"stock", casi siempre está mal planteado: lo que se cuenta son cupos de lote.

## Decisiones técnicas cerradas

Estas son decisiones ya tomadas. No proponer alternativas ni cambiarlas sin que se pida.

**Moneda y números** — Pesos chilenos, enteros, sin decimales. Guardar como `Integer`, nunca
`Float`. Los precios se guardan **netos**: el pedido muestra neto, IVA y total por separado.
El IVA es 19%.

**Cómo se redondea** — En este orden y no en otro:

1. `neto = truncar(gramos × precio por gramo)`
2. `iva = neto × 0,19`, redondeado medio hacia arriba
3. `total = neto + iva`

El cálculo se hace con `Decimal` y `ROUND_HALF_UP`. El `round()` de Python usa redondeo
bancario: con 3.828,50 devuelve 3.828 en vez de 3.829 y el total queda un peso corto.

**Gramos** — Se guardan como `Decimal`, nunca `Float`.

**Zona horaria y locale** — `America/Santiago`. `USE_TZ = True`, guardar en UTC, mostrar en
hora local. Formato de fecha `dd-mm-aaaa`. Toda la interfaz en español de Chile.

**Cómo se resuelve la tienda en cada petición** — Por el usuario autenticado, leído del JWT,
no por subdominio ni por un parámetro de la URL. Un `tienda_id` que venga en el cuerpo o en
la query string **no se confía nunca**: se ignora y se usa el del token. Para el catálogo
público de una tienda, la tienda va en la ruta (`/t/<slug>/...`) y solo expone datos publicados.

**Roles** — Cuatro, y no más:
- `admin_plataforma` — nosotros. Ve todas las tiendas. No se crea desde la interfaz.
- `dueno_tienda` — el vendedor suscrito. Ve y administra solo su tienda.
- `vendedor` — empleado del dueño. Igual que el dueño pero sin acceso a facturación
  ni a la gestión de usuarios.
- `comprador` — cliente final o mayorista. No pertenece a ninguna tienda.

**Tramos de precio del granel** — Los umbrales en gramos (medio kilo, kilo) tienen
prioridad. Si la cantidad no alcanza ninguno de ellos, se calcula un **monto de referencia**
con el precio del primer tramo y se aplica el tramo en pesos que ese monto alcance. Bajo
$20.000 de referencia, el pedido se rechaza. Los precios que entregó el cliente se usan tal
cual: no se redondean ni se "ordenan". Validar al guardar que los tramos de una misma lista
no se repitan.

**Los umbrales son inclusivos.** "Sobre 20 mil" incluye los $20.000 exactos: la comparación
es `>=`. Confirmado con el cliente el 27-09-2026.

**Aviso de conveniencia** — Cuando comprar más sale más barato que lo pedido (entre 893 y
999 g de línea hombre cuesta más que un kilo entero), el backend lo informa junto a la
cotización y el frontend lo muestra. No se cambia la cantidad por el comprador: se le avisa.

**Estados del pedido** — `borrador → confirmado → preparacion → entregado`, más `anulado`
alcanzable desde cualquiera menos `entregado`. Las transiciones válidas se definen en un solo
lugar del modelo; una transición no permitida es un error de validación, no un `assert`.

**Cupos** — Reemplazan al stock. Se descuentan al pasar el pedido a `confirmado`, no al
agregar al carrito. El descuento va dentro de una transacción con bloqueo de la fila del
lote (`select_for_update`), porque dos compradores pueden confirmar el último cupo a la vez.
Anular un pedido devuelve el cupo.

**Imágenes del catálogo** — En Cloudflare R2. Son públicas: se sirven por URL directa, sin
firmar. La base guarda solo la clave del objeto, nunca la URL completa. Validar tipo y tamaño
al subir. El nombre del archivo lo genera el sistema, nunca se usa el que envía el usuario.

## Carga masiva del catálogo

Es la carga de lotes, líneas de granel y fotos desde una planilla. **No** carga historial
de ventas: el cliente no lo tiene con ese detalle. Es una operación habitual del dueño,
porque el catálogo rota seguido.

Es el módulo que más va a fallar, porque el archivo lo hace una persona a mano.

- Nunca confiar en el orden de las columnas: mapear por nombre de encabezado, normalizado
  (minúsculas, sin acentos, sin espacios sobrantes).
- Una fila inválida **no aborta la carga**. Se acumulan los errores por número de fila y se
  devuelve un resumen: cuántas filas se cargaron, cuántas se rechazaron y por qué.
- La carga es idempotente: subir dos veces la misma planilla no duplica nada. La clave
  natural es (tienda, código del lote o de la línea).
- Un lote que no viene en el archivo **no se borra**. Solo se desactiva si el dueño lo marca
  explícitamente: una planilla incompleta no puede vaciar el catálogo.
- Guardar cada carga con su archivo original, fecha y usuario, para poder auditar de dónde
  salió cada dato.
- No hay historial real suficiente para entrenar. Se trabaja con datos sintéticos generados
  por nosotros, y **todo gráfico o métrica producido con ellos se rotula como tal** en la
  interfaz. Nunca mostrar un número sintético como si fuera del cliente.

## Los dos modelos y sus métricas

Son problemas distintos y **no se miden igual**. Confundirlos produce un número que parece
válido y no lo es.

| Modelo | Tipo de problema | Métricas | Línea base |
|---|---|---|---|
| Pronóstico de demanda mensual por categoría de lote | Regresión sobre serie de tiempo | MAPE, MAE, RMSE | Promedio móvil |
| Segmentación y riesgo de abandono de clientes | Clasificación sobre variables RFM | Precisión, exhaustividad, F1 | Regla por recencia |

Nunca usar accuracy, F1 ni matriz de confusión para el pronóstico. Todo modelo se contrasta
con su línea base: si no la supera, no se integra.

El pronóstico es **por categoría de lote**, no por lote: los de cupo único se venden una
sola vez y no forman una serie de tiempo. Los datos de entrenamiento son sintéticos,
calibrados con los montos reales de venta que entregó el cliente.

El **motor de recomendación de descuentos no es un tercer modelo**. Son reglas de negocio
que consumen las salidas de los dos anteriores. Sugiere; el vendedor aprueba. Nunca ejecuta
campañas por su cuenta.

## Alcance

Comprometido: marketplace multi-tienda, motor de precios por tramos para lotes y granel,
gestión de pedidos con checkout simulado, carga masiva de catálogo desde planillas, panel de
analítica, pronóstico de demanda, segmentación de clientes, recomendación de descuentos,
asistente conversacional del vendedor.

La **agenda de visitas** está construida pero el cliente no la confirmó. Queda congelada:
no se le suman funciones hasta cerrar el núcleo del negocio, y no se borra hasta que el
cliente responda.

**Fuera de alcance — no proponer ni implementar:**

- Pasarela de pagos real (Transbank, MercadoPago). El checkout queda simulado.
- Búsqueda visual de productos por imagen.
- Ejecución automática de campañas o envío de correos sin aprobación humana.

## Lo que no está decidido

Si el trabajo depende de uno de estos puntos, **preguntar antes de implementar**:

Pendientes con el cliente:

- Si confirma la agenda de visitas.
- Descuento por cantidad de lotes: desde cuántos y de cuánto. Los tramos 1–2, 3–5 y 6 o
  más los propusimos nosotros; el cliente nunca los dijo, así que **no se programan como
  reales**: quedan configurables por tienda.
- Cuánto tiempo se guarda un pedido que no se paga. Sin plazo, un lote de cupo único pedido
  y no pagado queda bloqueado para siempre.
- Si cualquiera puede comprar o el dueño aprueba a los compradores. De esto depende que el
  modelo `AprobacionMayorista` se mantenga, se adapte o se elimine, y si existe un precio
  mayorista distinto del normal.
- Si se pueden sumar líneas de granel para alcanzar un tramo, o cada línea va por su cuenta.

Pendientes del equipo:

- Qué proveedor de modelo de lenguaje usa el asistente conversacional, y con qué presupuesto.
- Si el asistente responde solo sobre datos de la tienda o también sobre el catálogo público.
- Cómo se cobra la suscripción del vendedor, si es que se modela en esta fase.
- Si el vendedor puede ver el pronóstico. En el código es un permiso de una línea.
- Qué entra a la demostración de noviembre y qué queda como trabajo futuro.
- Qué versión de PostgreSQL es la única: el diagrama dice 16 y el CI usa 17.

## Seguridad

**El repositorio es público.** Nada de credenciales en el código, en ningún momento.

- Claves, tokens y contraseñas van en variables de entorno. `.env` está en `.gitignore` y
  se mantiene un `.env.example` con los nombres pero sin valores.
- El asistente conversacional traduce texto libre del usuario en consultas sobre datos:
  es un vector de inyección. Su acceso se restringe por diseño a la tienda del usuario
  autenticado, y la entrada se valida.
- Autorización por rol en cada endpoint, no solo en la interfaz. Ocultar un botón en el
  frontend no protege nada.

## Errores y respuestas de la API

- Formato único de error: `{"error": {"codigo": "...", "mensaje": "...", "detalles": {...}}}`.
  El mensaje es para mostrar al usuario, en español. El código es para el frontend.
- Un error nunca filtra detalles internos: sin rutas de archivos, sin consultas SQL, sin
  trazas. `DEBUG = False` es el valor por defecto y solo se activa localmente.
- Listados paginados siempre, con un tope máximo de página. Un endpoint sin límite es un
  problema de rendimiento y de denegación de servicio.

## Pruebas

- Las fixtures base crean **siempre dos tiendas con datos**. Una prueba que corre con una sola
  tienda no puede detectar una fuga de aislamiento, que es el error más grave del sistema.
- Cada endpoint que lee datos de tienda lleva una prueba que se autentica como tienda A y
  espera `404` al pedir un recurso de la tienda B. **`404`, no `403`**: un `403` confirma que
  el recurso existe.
- El motor de precios por tramos se prueba en los bordes: justo bajo el umbral, justo en el
  umbral y sobre el último tramo. También el rechazo bajo los $20.000 de referencia y el
  aviso de conveniencia.

## Convenciones

- **Python** — PEP 8. **JavaScript/TypeScript** — ESLint.
- **Ramas** por funcionalidad, nunca commits directos a `main`.
- **Pull request con revisión del otro integrante** antes de integrar. Es la regla que
  evita que uno solo entienda una parte del sistema.
- **Criterio de terminado**: código revisado, pruebas unitarias en verde, desplegado en el
  ambiente de pruebas y documentación actualizada.
- Mensajes de commit en español, en imperativo: "agrega motor de precios escalonados".

## Equipo

- **Pedro Santibáñez** — frontend y seguridad. Interfaz, autenticación, autorización por
  rol, políticas de aislamiento y pruebas de control de acceso.
- **Daniel Azócar** — modelo de datos y Machine Learning. Esquema relacional, ingesta,
  los dos modelos predictivos y el motor de reglas.
- **Compartido** — backend en Django REST Framework, motor de precios, contenerización,
  despliegue y pruebas.

**Daniel es Product Owner y Pedro es Scrum Master.**

## Metodología

Scrum en cuatro sprints de tres semanas más un cierre. CRISP-DM estructura el trabajo
analítico, pero **no corre en paralelo**: cada fase del ciclo (comprensión del negocio,
comprensión de los datos, preparación, modelado, evaluación, despliegue) es un conjunto
de historias del mismo backlog, con la misma cadencia.

## Comandos

```bash
docker compose up -d              # levanta base de datos, backend y frontend
docker compose exec api pytest    # pruebas del backend
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
npm run lint                      # frontend
```

Ajustar los nombres de servicio cuando el docker-compose esté definido.
