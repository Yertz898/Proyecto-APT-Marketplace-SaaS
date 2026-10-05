import { leerError } from "@/lib/api/errores";
import { pedirConSesion } from "@/lib/api/sesion";
import type { PaginaDelPanel, ResumenDeInventario } from "@/lib/tipos-panel";

/*
 * El catálogo de la tienda, desde su panel.
 *
 * Es otro contrato que el de la vitrina y por eso otro archivo: acá aparece lo
 * desactivado y lo agotado, que es lo que el dueño necesita ver. La ruta no
 * nombra ninguna tienda porque sale del token.
 */

export async function obtenerCatalogoDelPanel(
  { pagina = 1, forma }: { pagina?: number; forma?: string } = {},
): Promise<PaginaDelPanel> {
  const consulta = new URLSearchParams({ pagina: String(pagina) });
  if (forma) {
    consulta.set("forma", forma);
  }

  const respuesta = await pedirConSesion(`/panel/productos?${consulta}`);
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as PaginaDelPanel;
}

export async function obtenerInventario(): Promise<ResumenDeInventario> {
  const respuesta = await pedirConSesion("/panel/inventario");
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as ResumenDeInventario;
}
