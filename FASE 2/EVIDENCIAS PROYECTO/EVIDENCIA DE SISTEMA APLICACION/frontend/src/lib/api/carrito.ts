import { leerError } from "@/lib/api/errores";
import { pedirConSesion } from "@/lib/api/sesion";
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
  // Va con la sesión si la hay: así el pedido queda a nombre del comprador y
  // el backend no le pide el RUT, que ya está en su cuenta. Sin sesión es una
  // compra como visitante, y el backend exige RUT, nombre y correo.
  const respuesta = await pedirConSesion(`/t/${slug}/pedidos/`, {
    method: "POST",
    body: JSON.stringify({ ...contacto, lineas }),
  });

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return respuesta.json();
}