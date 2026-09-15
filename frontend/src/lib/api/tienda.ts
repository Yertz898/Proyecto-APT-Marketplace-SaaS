import type { ContenidoTienda } from "@/lib/tipos";
import { contenidoLocalDeTienda } from "@/tiendas";

/**
 * Contenido de una tienda pública por su slug.
 *
 * Todavía no hay API: lee el contenido provisorio de src/tiendas/. Al conectar
 * el backend solo cambia el cuerpo de esta función.
 */
export async function obtenerTienda(slug: string): Promise<ContenidoTienda | null> {
  return contenidoLocalDeTienda(slug);
}
