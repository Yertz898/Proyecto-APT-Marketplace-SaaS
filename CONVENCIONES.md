# DealCommerce

Marketplace SaaS multi-tienda con analítica predictiva para PYMES del retail.
Proyecto de título (Capstone PTY4614, Duoc UC). Equipo de dos personas, 18 semanas.

Cliente piloto real: **Joyas_ye**, joyería con tienda física y canal en redes sociales
que vende al detalle y al por mayor. El dueño es hombre; referirse a él como "el cliente"
o "el dueño".

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
- **Producto** con **variantes** (material, talla, terminación). El stock vive en la
  variante, no en el producto.
- **Lista de precios escalonados** — tramos por volumen de compra. Un mismo producto
  tiene precio distinto según la cantidad. Esto es lo que resuelve la venta al detalle y
  al por mayor con un solo catálogo, y es el módulo con más lógica de negocio del sistema.
- **Pedido** — checkout **simulado**: se genera el pedido y se descuenta stock, pero no
  se cobra. El pago se coordina fuera de la plataforma.
- **Cliente comprador** — se le calculan variables de recencia, frecuencia y monto (RFM)
  para el modelo de segmentación.

## Decisiones técnicas cerradas

Estas son decisiones ya tomadas. No proponer alternativas ni cambiarlas sin que se pida.

**Moneda y números** — Pesos chilenos, enteros, sin decimales. Guardar como `Integer`, nunca
`Float`. El redondeo de un precio escalonado es hacia arriba al peso. Los precios se guardan
y se muestran **con IVA incluido**.

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

**Precio mayorista** — Un comprador ve los tramos mayoristas solo si el dueño de la tienda lo
marcó como mayorista aprobado. Un comprador no aprobado ve únicamente el precio de detalle.
Esto es una regla de autorización, no un detalle de interfaz: se aplica en el backend al
calcular el precio, no ocultando el tramo en el frontend.

**Tramos de precio** — Definidos por cantidad mínima, sin solaparse. Se aplica el tramo de
mayor cantidad mínima que la cantidad pedida alcance. Si no alcanza ninguno, precio de
detalle. Validar al guardar que los tramos de una lista no se solapen.

**Estados del pedido** — `borrador → confirmado → preparacion → entregado`, más `anulado`
alcanzable desde cualquiera menos `entregado`. Las transiciones válidas se definen en un solo
lugar del modelo; una transición no permitida es un error de validación, no un `assert`.

**Stock** — Se descuenta al pasar a `confirmado`, no al agregar al carrito. El descuento va
dentro de una transacción con bloqueo de la fila de la variante
(`select_for_update`), porque dos compradores pueden confirmar la última unidad a la vez.
Anular un pedido devuelve el stock.

**Imágenes de producto** — En Cloudflare R2. Son públicas: se sirven por URL directa, sin
firmar. La base guarda solo la clave del objeto, nunca la URL completa. Validar tipo y tamaño
al subir. El nombre del archivo lo genera el sistema, nunca se usa el que envía el usuario.

## Ingesta de planillas

Es el módulo que más va a fallar, porque el archivo lo hace una persona a mano.

- Nunca confiar en el orden de las columnas: mapear por nombre de encabezado, normalizado
  (minúsculas, sin acentos, sin espacios sobrantes).
- Una fila inválida **no aborta la carga**. Se acumulan los errores por número de fila y se
  devuelve un resumen: cuántas filas se cargaron, cuántas se rechazaron y por qué.
- La carga es idempotente: subir dos veces la misma planilla no duplica las ventas. La clave
  natural es (tienda, documento de venta, línea).
- Guardar cada carga con su archivo original, fecha y usuario, para poder auditar de dónde
  salieron los datos que alimentan los modelos.
- No hay historial real suficiente para entrenar. Se trabaja con datos sintéticos generados
  por nosotros, y **todo gráfico o métrica producido con ellos se rotula como tal** en la
  interfaz. Nunca mostrar un número sintético como si fuera del cliente.

## Los dos modelos y sus métricas

Son problemas distintos y **no se miden igual**. Confundirlos produce un número que parece
válido y no lo es.

| Modelo | Tipo de problema | Métricas | Línea base |
|---|---|---|---|
| Pronóstico de demanda mensual por producto | Regresión sobre serie de tiempo | MAPE, MAE, RMSE | Promedio móvil |
| Segmentación y riesgo de abandono de clientes | Clasificación sobre variables RFM | Precisión, exhaustividad, F1 | Regla por recencia |

Nunca usar accuracy, F1 ni matriz de confusión para el pronóstico. Todo modelo se contrasta
con su línea base: si no la supera, no se integra.

El **motor de recomendación de descuentos no es un tercer modelo**. Son reglas de negocio
que consumen las salidas de los dos anteriores. Sugiere; el vendedor aprueba. Nunca ejecuta
campañas por su cuenta.

## Alcance

Comprometido: marketplace multi-tienda, motor de precios escalonados, gestión de pedidos con
checkout simulado, ingesta del historial de ventas desde planillas, panel de analítica,
pronóstico de demanda, segmentación de clientes, recomendación de descuentos, asistente
conversacional del vendedor.

**Fuera de alcance — no proponer ni implementar:**

- Pasarela de pagos real (Transbank, MercadoPago). El checkout queda simulado.
- Búsqueda visual de productos por imagen.
- Ejecución automática de campañas o envío de correos sin aprobación humana.

## Lo que no está decidido

Si el trabajo depende de uno de estos puntos, **preguntar antes de implementar**:

- Qué proveedor de modelo de lenguaje usa el asistente conversacional, y con qué presupuesto.
- Si el asistente responde solo sobre datos de la tienda o también sobre el catálogo público.
- Cómo se cobra la suscripción del vendedor, si es que se modela en esta fase.
- Quién es Product Owner y quién Scrum Master en el equipo.

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
- El motor de precios escalonados se prueba en los bordes: cantidad justo bajo el tramo, justo
  en el tramo, y sobre el último tramo.

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

## Metodología

Scrum con sprints de dos semanas. CRISP-DM estructura el trabajo analítico, pero **no corre
en paralelo**: cada fase del ciclo (comprensión del negocio, comprensión de los datos,
preparación, modelado, evaluación, despliegue) es un conjunto de historias del mismo
backlog, con la misma cadencia.

## Comandos

```bash
docker compose up -d              # levanta base de datos, backend y frontend
docker compose exec api pytest    # pruebas del backend
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
npm run lint                      # frontend
```

Ajustar los nombres de servicio cuando el docker-compose esté definido.
