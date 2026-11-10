# Ventas y pedidos

Qué le pasa a un pedido desde que el comprador lo confirma, y de dónde sale cada número
del panel de ventas.

## El recorrido del pedido

El pago **no pasa por la plataforma**. La tienda piloto cobra por transferencia y coordina
por WhatsApp, así que lo que el sistema hace es registrar el compromiso y seguirlo. Eso
explica casi todas las decisiones de abajo.

```
cotizar  →  confirmar  →  PENDIENTE  →  CONFIRMADO  →  ENTREGADO
                                ↓             ↓
                            CANCELADO     CANCELADO
```

**Cotizar no escribe nada.** El carrito lo llama en cada cambio de cantidad. Los precios
salen de `precios.servicios.cotizar`, que es el mismo motor que usa la ficha del producto;
el carrito no tiene aritmética propia. Cuando la tenía, la ficha mostraba el precio por
tramo y el carrito cobraba el precio base.

**Confirmar vuelve a cotizar.** No se confía en lo que manda el navegador: entre que el
comprador mira el total y aprieta el botón pasa tiempo, y en ese rato el precio pudo
cambiar o el último lote pudo venderse. Si alguna línea ya no se puede pedir, no se crea
nada: la operación es una transacción entera.

### Los cuatro estados

| Estado | Qué significa | Cuenta como venta |
|---|---|---|
| `PENDIENTE` | El comprador lo confirmó. Falta coordinar el pago. | No |
| `CONFIRMADO` | La tienda lo dio por cerrado. | Sí |
| `ENTREGADO` | Ya se entregó. | Sí |
| `CANCELADO` | No se concretó. Devuelve el inventario. | Nunca |

Los estados **avanzan y no retroceden**. De pendiente se confirma o se anula; de confirmado
se entrega o se anula; lo entregado o anulado no se mueve más. Deshacer una entrega es una
corrección de historia y para eso no alcanza un botón sin registro de quién lo apretó.

### Inventario

Se descuenta **al confirmar el pedido**, no al agregar al carrito: un carrito abandonado no
puede dejar el catálogo bloqueado.

El descuento va con la fila del producto bloqueada (`select_for_update`). Es lo que impide
que dos compradores simultáneos se lleven el mismo último lote: el segundo espera a que el
primero termine y entonces ve el stock ya descontado.

Anular repone con el mismo bloqueo, y **anular dos veces no repone dos veces**. Un producto
que no lleva inventario no descuenta ni repone nada, porque la tienda no sabe cuánto le
queda.

### Precios congelados

Cada línea guarda el precio unitario, el neto, el IVA y el total **del momento en que se
confirmó**. No se leen del catálogo al mostrar el pedido. Si se leyeran, subir un precio
reescribiría lo que alguien ya pagó.

### El enlace de WhatsApp

Se arma con el campo `whatsapp` de la tienda y lleva el folio, el detalle y el total.
**Una tienda sin WhatsApp configurado no recibe enlace.** Un enlace a un número que no es
de la tienda es peor que no tener enlace: el comprador cree que avisó y nadie leyó nada.

## Los indicadores del panel de ventas

Todo lo de esta pantalla está **medido**: sale de sumar pedidos que existen. El pronóstico
de demanda y los segmentos de compradores son estimaciones y van en sus propias pantallas
(ver `analitica.md`); en una sola nadie distinguiría qué número se midió y cuál se estimó.

### Ventas del mes

Suma de `total_neto`, `total_iva` y `total` de los pedidos **confirmados y entregados** del
mes calendario en curso, más cuántos son.

El mes se corta en **hora de Chile y no en UTC**. A las 21:30 del 30 de noviembre en Chile
ya es 1 de diciembre en UTC, y las ventas del mes se cortarían un día antes.

### Por coordinar

Los pedidos `PENDIENTE`, con su monto. Van **aparte y no sumados a las ventas**, porque
entre que alguien confirma un pedido y transfiere puede no pasar nada. Contarlos como
venta infla el mes con plata que no llegó.

### Mes anterior y variación

El mismo cálculo sobre el mes calendario anterior. La variación es
`(este mes − anterior) / anterior`.

**Si el mes anterior fue cero, no hay variación**: se muestra el monto sin porcentaje.
Mostrar «+100%» donde antes no había ventas es inventar una comparación.

### Lo que más te dejó

Los cinco productos con mayor neto vendido en los **últimos 90 días**, ordenados por dinero
y **no por unidades**. Son cosas distintas: diez lotes de aros baratos no valen lo mismo que
dos de plata colombiana, y el dueño reparte su atención por lo segundo.

Noventa días y no un mes porque un mes es poca ventana para una tienda mayorista que vende
por lotes: un lote que no se vendió en noviembre no es necesariamente un lote detenido.

### Sin movimiento

Productos **publicados** que no se vendieron en esos 90 días, del más antiguo al más nuevo.

Se dejan fuera dos grupos a propósito:

- **Los publicados dentro de la ventana.** Un lote que entró al catálogo la semana pasada
  no es un lote detenido: nunca tuvo tiempo. Marcarlo empujaría al dueño a rebajar algo que
  todavía no se ofreció.
- **Los desactivados.** Ya están fuera de la vitrina; no hay nada que decidir sobre ellos.

Cada uno dice **hace cuánto fue su última venta**, o que nunca se vendió. Son dos problemas
distintos: uno es un producto que dejó de salir y el otro es uno que nunca salió.

Los pedidos anulados no cuentan como venta acá tampoco. Si contaran, un lote cuyo único
pedido se anuló parecería recién vendido.
