import type { IdentidadTienda } from "@/lib/tipos";

/*
 * Identidad de la tienda pública.
 *
 * La tienda es datos, no código: nombre, logo, banner, colores y redes vienen
 * del backend según el slug de la URL.
 *
 * Nota para cuando el frontend corra dentro de Docker: esta llamada se hace
 * desde el servidor de Next, así que la dirección tendría que ser la del
 * servicio `api` y no localhost.
 */

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

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
