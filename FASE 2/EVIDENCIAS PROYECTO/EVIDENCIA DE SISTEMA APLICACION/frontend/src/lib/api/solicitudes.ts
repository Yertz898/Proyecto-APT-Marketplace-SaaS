import { API_NAVEGADOR as API } from "./base";
import { errorDeConexion, leerError } from "./errores";

/*
 * Solicitudes de acceso a la plataforma.
 *
 * Sale del navegador y no pide sesión: es justamente el formulario de quien
 * todavía no tiene cuenta.
 */

export type SolicitudDeAcceso = {
  negocio: string;
  nombre: string;
  email: string;
  telefono: string;
  mensaje?: string;
};

export async function pedirAcceso(datos: SolicitudDeAcceso): Promise<void> {
  let respuesta: Response;

  try {
    respuesta = await fetch(`${API}/solicitudes-de-acceso`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
  } catch {
    throw errorDeConexion();
  }

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }
}
