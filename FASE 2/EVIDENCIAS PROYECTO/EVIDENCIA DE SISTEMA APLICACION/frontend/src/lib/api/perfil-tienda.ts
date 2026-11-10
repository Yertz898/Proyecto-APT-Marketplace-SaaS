import { leerError } from "@/lib/api/errores";
import { pedirConSesion } from "@/lib/api/sesion";
import type { CambiosDelPerfil, PerfilDeTienda } from "@/lib/tipos-panel";

/*
 * Perfil de la tienda en el panel.
 *
 * La ruta no nombra ninguna tienda, y no es un olvido: el backend la saca del
 * token. No existe la petición que pida o cambie el perfil de otra tienda.
 */

const RUTA = "/panel/tienda";

export async function obtenerPerfil(): Promise<PerfilDeTienda> {
  const respuesta = await pedirConSesion(RUTA);

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as PerfilDeTienda;
}

/**
 * Guarda los cambios del perfil.
 *
 * Va siempre como multipart porque el logo y el banner son archivos, y mezclar
 * dos formas de enviar según lo que cambió duplicaría el camino por nada.
 */
export async function guardarPerfil(cambios: CambiosDelPerfil): Promise<PerfilDeTienda> {
  const cuerpo = new FormData();
  for (const [campo, valor] of Object.entries(cambios)) {
    if (valor !== undefined) {
      cuerpo.append(campo, valor);
    }
  }

  const respuesta = await pedirConSesion(RUTA, { method: "PATCH", body: cuerpo });

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as PerfilDeTienda;
}
