import type { CotizacionGranel, LineaGranel, Lote, PaginaDeLotes } from "@/lib/tipos";

import { API_SERVIDOR as API } from "./base";

/*
 * Catálogo público de una tienda: lotes y líneas de granel.
 *
 * El backend entrega el precio neto, el IVA y el total ya calculados, y
 * redacta el mínimo de compra. El navegador no hace aritmética de dinero: los
 * tramos dependen del pedido completo y un cupo puede agotarse mientras el
 * comprador decide.
 *
 * Una tienda o un código que no existen responden 404, igual que un lote
 * inactivo, agotado o de otra tienda. Acá eso se traduce a `null` o a una
 * página vacía, nunca a una excepción: la vitrina muestra "no encontrado" en
 * vez de caerse.
 *
 * Pendiente del Sprint 3: `cotizarGranel`.
 */

const VACIA = (pagina: number): PaginaDeLotes => ({
  lotes: [],
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
      // El catálogo cambia cuando el dueño lo edita o se agota un cupo.
      next: { revalidate: 30 },
    });

    return respuesta.ok ? ((await respuesta.json()) as T) : null;
  } catch {
    // Con el backend apagado la vitrina responde vacío en vez de caerse.
    return null;
  }
}

export async function obtenerLotes(slug: string, pagina: number): Promise<PaginaDeLotes> {
  const tienda = encodeURIComponent(slug);
  const datos = await pedir<PaginaDeLotes>(`/t/${tienda}/lotes?pagina=${pagina}`);

  return datos ?? VACIA(pagina);
}

export async function obtenerLote(slug: string, codigo: string): Promise<Lote | null> {
  const tienda = encodeURIComponent(slug);
  return pedir<Lote>(`/t/${tienda}/lotes/${encodeURIComponent(codigo)}`);
}

export async function obtenerLineasGranel(slug: string): Promise<LineaGranel[]> {
  const datos = await pedir<LineaGranel[]>(`/t/${encodeURIComponent(slug)}/granel`);
  return datos ?? [];
}

export async function obtenerLineaGranel(slug: string, codigo: string): Promise<LineaGranel | null> {
  const tienda = encodeURIComponent(slug);
  return pedir<LineaGranel>(`/t/${tienda}/granel/${encodeURIComponent(codigo)}`);
}

/** El precio lo calcula el backend; el navegador solo muestra lo que devuelve. */
export async function cotizarGranel(
  slug: string,
  codigo: string,
  gramos: number,
): Promise<CotizacionGranel> {
  void slug;
  void gramos;
  throw new ApiPendiente(`POST /t/{slug}/granel/${codigo}/cotizar`);
}
