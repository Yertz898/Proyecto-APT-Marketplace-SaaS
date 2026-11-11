# Arquitectura

Cómo está armado el sistema y, sobre todo, **dónde está escrita cada regla**. Una regla
escrita en dos partes es una regla que en algún momento va a decir dos cosas distintas.

## Las piezas

```
navegador ──► Next.js ──► Django REST Framework ──► PostgreSQL
                 │                 │
                 └── Cloudflare R2 ┘   (fotos de producto)
```

| Pieza | Qué decide |
|---|---|
| **Next.js** | Cómo se ve y qué se muestra. No calcula precios ni decide permisos. |
| **Django REST Framework** | Qué puede ver y hacer cada quien, y cuánto cuesta cada cosa. |
| **PostgreSQL** | Los invariantes que no pueden depender de que el código los recuerde. |
| **Cloudflare R2** | Las fotos. La base guarda la referencia, nunca el binario. |

El frontend tiene **dos direcciones distintas del backend** y no es un descuido: el
servidor de Next llega a Django por la red interna de Docker (`api:8000`) y el navegador
por el puerto publicado (`localhost:8000`). Una sola dirección no puede servir a los dos.

## El aislamiento entre tiendas

Es el invariante del producto: DealCommerce arrienda locales a PYMES distintas y ninguna
puede ver los datos de otra. Está sostenido en cuatro capas, y cada una supone que la
anterior podría fallar.

### 1. El modelo

Todo lo que pertenece a una tienda hereda de `ModeloDeTienda` (`apps/core/models.py`), que
trae el campo `tienda` con su índice. No depende de que alguien recuerde agregarlo.

### 2. El manager

`ManagerDeTienda` (`apps/core/managers.py`) es el manager por omisión de esos modelos y
trae `de_usuario(usuario)`, que es **el único lugar donde está escrito quién ve qué**:

- Administrador de plataforma: todas las tiendas.
- Dueño y vendedor: solo la suya.
- Cualquier otro caso, incluido el anónimo: nada.

Devuelve vacío en vez de lanzar un error, a propósito: así una vista mal escrita muestra
una lista vacía o responde 404, y nunca datos de otra tienda. El modo de fallo apunta
hacia el lado seguro.

### 3. Los mixins de vista

`MixinTiendaDelUsuario` para el panel y `MixinTiendaPublica` para la vitrina
(`apps/core/mixins.py`). Las vistas heredan de ahí en vez de repetir el filtro.

**La tienda sale del token, nunca de la petición.** Un `tienda_id` en el cuerpo o en la
query string no se confía: es un número que cualquiera puede cambiar. En la vitrina sale
del `slug` de la URL, que es público por definición.

`perform_create` pone la tienda del usuario en todo objeto nuevo, ignorando la que venga
en el cuerpo.

### 4. Las pruebas

Toda funcionalidad que lea datos de tienda lleva su prueba marcada
`@pytest.mark.aislamiento`, **en los dos sentidos**: que A no ve lo de B y que B no ve lo
de A. Una sola dirección deja pasar un filtro escrito al revés.

```bash
docker compose exec api pytest -m aislamiento
```

### 404 y no 403

Lo que no es de tu tienda responde **404**. Un 403 confirmaría que el recurso existe en
otra tienda, que ya es información que no corresponde dar: con un 403 se puede recorrer
el catálogo ajeno sin verlo, contándolo.

La excepción es el propio negocio: a un vendedor que intenta escribir donde solo puede
leer se le responde 403, porque es su tienda y la ve igual.

## Dónde vive cada regla

| Regla | Dónde, una sola vez |
|---|---|
| Quién ve qué | `apps/core/managers.py` |
| Qué puede hacer cada rol | `apps/core/permissions.py` |
| El IVA y el redondeo | `apps/precios/dinero.py` |
| Qué precio corresponde a una cantidad | `apps/precios/servicios.py` |
| Qué cuenta como venta | `apps/analitica/ventas.py` |

El motor de precios es el ejemplo de por qué esto importa. Lo usan la ficha del producto,
el carrito y el pedido. Cuando el carrito tuvo su propia aritmética, la ficha mostraba el
precio por tramo y el carrito cobraba el precio base: 30% de diferencia, en la misma
visita y en dos pantallas seguidas. Está contado en `bitacora/sprint-3.md`.

## Lo que sostiene la base de datos

Hay invariantes que no se delegan al código de aplicación, porque una vista mal escrita no
puede poder romperlos:

- El stock no puede quedar negativo, y un producto que dice controlar inventario no puede
  tener stock nulo (`CheckConstraint`).
- El precio y la cantidad mínima son mayores que cero.
- La unidad de medida tiene que corresponder a la forma de venta.
- El código de producto y el nombre de categoría son únicos **por tienda**, no globalmente:
  dos tiendas pueden llamar igual a sus cosas.

## Las dos entradas

El sistema tiene dos puertas y no se mezclan.

| | DealCommerce | Cada tienda |
|---|---|---|
| Dirección | `/panel` | `/t/<slug>` |
| Para quién | Plataforma, dueños y vendedores | Quien compra en esa tienda |
| Aspecto | La marca de DealCommerce | La identidad de esa tienda |
| Crear cuenta | No: las crea la plataforma | Sí |

La identidad visual de cada tienda se aplica con variables CSS que el servidor escribe en
el atributo `data-identidad` del contenedor de la vitrina. El comprador elige claro u
oscuro y la hoja de estilos decide qué versión de la paleta usar; el tema vive en un
atributo del `<html>` y no en el estado de React, para que un guion lo pueda dejar puesto
antes de pintar.

## Qué no hace el frontend

- **No calcula precios.** Los pide. Si los calculara, el precio saldría de un lugar que el
  comprador puede editar.
- **No decide permisos.** El candado y el ocultamiento de secciones son cortesía: quien
  decide es el backend en cada endpoint. Un plan o un rol cambiados en el navegador no
  abren ninguna sección.
- **No redacta las cifras del asistente.** Las arma el backend con las mismas funciones que
  pintan el panel, así que el asistente y las pantallas no se pueden contradecir.

## El analítico

Está separado en tres módulos dentro de `apps/analitica/`, y la separación responde a qué
tan confiable es cada número:

- `ventas.py` — **hechos**: suma pedidos que existen.
- `pronostico.py` — **estimación**: línea base de promedio móvil.
- `segmentos.py` — **estimación**: regla por recencia.

No comparten pantalla, a propósito. En una sola, nadie distinguiría qué está medido y qué
está proyectado. Los detalles y los límites de los datos están en `analitica.md`.
