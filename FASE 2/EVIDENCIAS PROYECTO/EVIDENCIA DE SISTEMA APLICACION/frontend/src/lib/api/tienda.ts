import type { IdentidadTienda } from "@/lib/tipos";

import { API_SERVIDOR as API } from "./base";

/*
 * Identidad de la tienda pública.
 *
 * La tienda es datos, no código: nombre, logo, banner, colores y redes vienen
 * del backend según el slug de la URL.
 */

export async function obtenerIdentidadTienda(slug: string): Promise<IdentidadTienda | null> {
  try {
    const respuesta = await fetch(`${API}/t/${encodeURIComponent(slug)}/tienda`, {
      // La identidad cambia poco; un minuto de caché evita una consulta por
      // cada página que visita el comprador.
      next: { revalidate: 60 },
    });

    if (!respuesta.ok) {
      return null;
    }

    return (await respuesta.json()) as IdentidadTienda;
  } catch {
    // Con el backend apagado la tienda responde 404 en vez de caerse.
    return null;
  }
}
