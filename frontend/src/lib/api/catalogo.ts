import type { CotizacionGranel, LineaGranel, Lote, PaginaDeLotes } from "@/lib/tipos";

/*
 * Catálogo público de una tienda: lotes y líneas de granel.
 *
 * El backend todavía no existe. Los listados devuelven vacío y las fichas null,
 * para que las pantallas se construyan contra la forma final de los datos.
 *
 * Endpoints a implementar:
 *   GET  /t/{slug}/lotes?pagina=
 *   GET  /t/{slug}/lotes/{codigo}
 *   GET  /t/{slug}/granel
 *   GET  /t/{slug}/granel/{codigo}
 *   POST /t/{slug}/granel/{codigo}/cotizar
 *
 * Recordatorios al implementarlos (ver CONVENCIONES.md):
 * - Solo se exponen datos publicados de esa tienda.
 * - El precio del granel lo calcula el backend, incluido el aviso de
 *   conveniencia y el rechazo por bajo el mínimo.
 * - Las URLs de las fotos vienen de Cloudflare R2; hay que declarar ese dominio
 *   en images.remotePatterns de next.config.ts antes de que lleguen imágenes.
 */

export class ApiPendiente extends Error {
  constructor(endpoint: string) {
    super(`Esta función todavía no está conectada: falta implementar ${endpoint} en el backend.`);
    this.name = "ApiPendiente";
  }
}

export async function obtenerLotes(slug: string, pagina: number): Promise<PaginaDeLotes> {
  void slug;
  return { lotes: [], paginaActual: pagina, totalPaginas: 0 };
}

export async function obtenerLote(slug: string, codigo: string): Promise<Lote | null> {
  void slug;
  void codigo;
  return null;
}

export async function obtenerLineasGranel(slug: string): Promise<LineaGranel[]> {
  void slug;
  return [];
}

export async function obtenerLineaGranel(slug: string, codigo: string): Promise<LineaGranel | null> {
  void slug;
  void codigo;
  return null;
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
