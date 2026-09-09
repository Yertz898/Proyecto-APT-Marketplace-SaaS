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
  autenticarse como tienda A e intentar leer datos de la tienda B debe fallar.

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

## Seguridad

**El repositorio es público.** Nada de credenciales en el código, en ningún momento.

- Claves, tokens y contraseñas van en variables de entorno. `.env` está en `.gitignore` y
  se mantiene un `.env.example` con los nombres pero sin valores.
- El asistente conversacional traduce texto libre del usuario en consultas sobre datos:
  es un vector de inyección. Su acceso se restringe por diseño a la tienda del usuario
  autenticado, y la entrada se valida.
- Autorización por rol en cada endpoint, no solo en la interfaz. Ocultar un botón en el
  frontend no protege nada.

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
