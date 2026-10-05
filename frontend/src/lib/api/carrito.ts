import { ApiPendiente } from "@/lib/api/catalogo";
import type { CarritoCotizado, LineaCarrito, PedidoConfirmado } from "@/lib/tipos";

/*
 * Carrito y pedido.
 *
 * El carrito del navegador guarda solo referencias y cantidades. Los precios,
 * los totales y el aviso del próximo tramo los calcula el backend cada vez, por
 * dos razones: el tramo que se aplica depende del pedido completo, y el stock
 * puede agotarse mientras el comprador decide.
 *
 * Endpoints a implementar:
 *   POST /t/{slug}/carrito/cotizar
 *   POST /t/{slug}/pedidos
 *
 * Al implementarlos (CONVENCIONES.md):
 * - El checkout es simulado: se genera el pedido y se descuenta stock, pero no
 *   se cobra. El pago se coordina fuera de la plataforma.
 * - El stock se descuenta al pasar a `confirmado`, solo en los productos que lo
 *   controlan, dentro de una transacción con bloqueo de la fila: dos
 *   compradores pueden confirmar la última unidad a la vez.
 * - Una línea rechazada (sin stock, bajo el mínimo) no bota el resto del
 *   carrito: viene marcada y el comprador decide.
 */

export async function cotizarCarrito(slug: string, lineas: LineaCarrito[]): Promise<CarritoCotizado> {
  void slug;
  void lineas;
  throw new ApiPendiente("POST /t/{slug}/carrito/cotizar");
}

export async function confirmarPedido(slug: string, lineas: LineaCarrito[]): Promise<PedidoConfirmado> {
  void slug;
  void lineas;
  throw new ApiPendiente("POST /t/{slug}/pedidos");
}
