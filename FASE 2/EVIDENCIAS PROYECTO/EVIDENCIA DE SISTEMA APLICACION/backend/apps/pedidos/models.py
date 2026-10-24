"""
Pedidos con checkout simulado.

Se genera el pedido y se descuentan los cupos de los lotes, pero no se cobra:
el pago se coordina fuera de la plataforma. No hay pasarela de pagos real y no
se va a agregar (está fuera de alcance).

El descuento de cupos va dentro de una transacción con `select_for_update`
sobre el lote, porque dos compradores pueden confirmar el último cupo a la vez.
Anular un pedido devuelve el cupo.

Al confirmar, el precio se recalcula en el backend. El total que manda el
navegador no se usa nunca.
"""
