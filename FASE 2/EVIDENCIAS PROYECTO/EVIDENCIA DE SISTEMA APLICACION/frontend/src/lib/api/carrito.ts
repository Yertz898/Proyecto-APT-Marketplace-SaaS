import type {
  CarritoCotizado,
  DatosDeContacto,
  LineaCarrito,
  PedidoConfirmado,
} from "@/lib/tipos";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function cotizarCarrito(slug: string, lineas: LineaCarrito[]): Promise<CarritoCotizado> {
  const respuesta = await fetch(`${API_URL}/t/${slug}/carrito/cotizar/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ lineas }),
  });

  if (!respuesta.ok) {
    const errorData = await respuesta.json().catch(() => null);
    throw new Error(errorData?.error || errorData?.detail || "No se pudo cotizar el carrito.");
  }

  return respuesta.json();
}

export async function confirmarPedido(
  slug: string,
  lineas: LineaCarrito[],
  contacto: DatosDeContacto,
): Promise<PedidoConfirmado> {
  const respuesta = await fetch(`${API_URL}/t/${slug}/pedidos/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ...contacto, lineas }),
  });

  if (!respuesta.ok) {
    const errorData = await respuesta.json().catch(() => null);
    throw new Error(errorData?.error || errorData?.detail || "No se pudo confirmar el pedido.");
  }

  return respuesta.json();
}