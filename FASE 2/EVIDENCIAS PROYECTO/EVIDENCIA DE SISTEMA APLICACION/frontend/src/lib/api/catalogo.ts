import type {
  Cotizacion,
  FormaDeVenta,
  PaginaDeProductos,
  Producto,
} from "@/lib/tipos";

import { API_NAVEGADOR, API_SERVIDOR as API } from "./base";

/*
 * Catálogo público de una tienda.
 *
 * Un solo endpoint para las tres formas de venta. La vitrina agrupa por forma
 * de venta, y qué formas mostrar sale de `obtenerFormasDeVenta`: no hay una
 * lista escrita acá, porque entonces una tienda nueva obligaría a tocar el
 * frontend.
 *
 * El backend entrega el precio neto, el IVA y el total ya calculados, y redacta
 * el mínimo de compra. El navegador no hace aritmética de dinero: los tramos
 * dependen del pedido completo y el stock puede agotarse mientras el comprador
 * decide.
 *
 * Una tienda o un código que no existen responden 404, igual que un producto
 * inactivo, agotado o de otra tienda. Acá eso se traduce a `null` o a una
 * página vacía, nunca a una excepción: la vitrina muestra "no encontrado" en
 * vez de caerse.
 */

const VACIA = (pagina: number): PaginaDeProductos => ({
  productos: [],
  paginaActual: pagina,
  totalPaginas: 0,
});

export class ApiPendiente extends Error {
  constructor(endpoint: string) {
    super(`Esta función todavía no está conectada: falta implementar ${endpoint} en el backend.`);
    this.name = "ApiPendiente";
  }
}

async function pedir<T>(ruta: string): Promise<T | null> {
  try {
    const respuesta = await fetch(`${API}${ruta}`, {
      // El catálogo cambia cuando el dueño lo edita o se agota el stock.
      next: { revalidate: 30 },
    });

    return respuesta.ok ? ((await respuesta.json()) as T) : null;
  } catch {
    // Con el backend apagado la vitrina responde vacío en vez de caerse.
    return null;
  }
}

/** Qué formas de venta usa esta tienda. Con esto la vitrina arma sus pestañas. */
export async function obtenerFormasDeVenta(slug: string): Promise<FormaDeVenta[]> {
  return (await pedir<FormaDeVenta[]>(`/t/${slug}/formas-de-venta`)) ?? [];
}

export async function obtenerProductos(
  slug: string,
  { pagina = 1, forma }: { pagina?: number; forma?: string } = {},
): Promise<PaginaDeProductos> {
  const consulta = new URLSearchParams({ pagina: String(pagina) });
  if (forma) {
    consulta.set("forma", forma);
  }

  return (
    (await pedir<PaginaDeProductos>(`/t/${slug}/productos?${consulta}`)) ?? VACIA(pagina)
  );
}

export async function obtenerProducto(
  slug: string,
  codigo: string,
): Promise<Producto | null> {
  return pedir<Producto>(`/t/${slug}/productos/${encodeURIComponent(codigo)}`);
}

/**
 * Qué cuesta llevar esta cantidad.
 *
 * Sale del navegador y no del servidor de Next —la pide el comprador mientras
 * escribe—, así que usa la dirección pública de la API.
 *
 * Un rechazo no es un error: viene con 200 y el motivo adentro, para mostrarlo
 * donde corresponde en vez de romper la pantalla.
 */
export async function cotizar(
  slug: string,
  codigo: string,
  cantidad: number,
): Promise<Cotizacion> {
  const respuesta = await fetch(
    `${API_NAVEGADOR}/t/${slug}/productos/${encodeURIComponent(codigo)}/cotizar`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cantidad }),
    },
  );

  if (!respuesta.ok) {
    const { leerError } = await import("@/lib/api/errores");
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as Cotizacion;
}
