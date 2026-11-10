import { leerError } from "@/lib/api/errores";
import { pedirConSesion } from "@/lib/api/sesion";
import type { EstadoPedido, PedidoDelPanel } from "@/lib/tipos-panel";

/*
 * Los pedidos de la tienda, desde el panel.
 *
 * La tienda no viaja en ninguna de estas rutas: sale del token. Un
 * identificador de tienda en la URL es algo que se puede cambiar a mano, y
 * acá se está pidiendo lo que compró gente real.
 */

async function pedir(ruta: string, opciones?: RequestInit): Promise<Response> {
  const respuesta = await pedirConSesion(ruta, opciones);
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }
  return respuesta;
}

export async function obtenerPedidos(): Promise<PedidoDelPanel[]> {
  return (await (await pedir("/panel/pedidos/")).json()) as PedidoDelPanel[];
}

/**
 * Cambia el estado de un pedido y devuelve cómo quedó.
 *
 * Pasarlo a `CANCELADO` devuelve al catálogo el inventario que tenía
 * reservado; el backend lo hace con la fila bloqueada.
 */
export async function cambiarEstadoDePedido(
  id: number,
  estado: EstadoPedido,
): Promise<PedidoDelPanel> {
  const respuesta = await pedir(`/panel/pedidos/${id}/estado/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado }),
  });
  return (await respuesta.json()) as PedidoDelPanel;
}
