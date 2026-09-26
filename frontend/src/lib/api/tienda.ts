import type { IdentidadTienda } from "@/lib/tipos";

/*
 * Identidad de la tienda pública.
 *
 * La tienda es datos, no código: nombre, logo, banner, colores y redes vienen
 * del backend según el slug de la URL. Mientras no exista la API no hay tienda
 * que mostrar, y las páginas responden 404.
 *
 * Endpoint a implementar:
 *   GET /t/{slug}/tienda
 */
export async function obtenerIdentidadTienda(slug: string): Promise<IdentidadTienda | null> {
  void slug;
  return null;
}
