import { API_NAVEGADOR as API } from "@/lib/api/base";
import { errorDeConexion, leerError } from "@/lib/api/errores";
import { borrarSesion, guardarAcceso, guardarSesion, instantanea, type Sesion } from "@/lib/sesion";
import type { UsuarioSesion } from "@/lib/tipos";

/*
 * Sesión contra el backend.
 *
 * Estas llamadas salen del navegador y no del servidor de Next, así que usan la
 * dirección pública de la API.
 */

type RespuestaDeSesion = {
  access: string;
  refresh: string;
  usuario: UsuarioSesion;
};

async function pedir(ruta: string, cuerpo: unknown, cabeceras: HeadersInit = {}): Promise<Response> {
  try {
    return await fetch(`${API}${ruta}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...cabeceras },
      body: JSON.stringify(cuerpo),
    });
  } catch {
    throw errorDeConexion();
  }
}

/** Entra con correo y contraseña, y deja la sesión guardada. */
export async function iniciarSesion(email: string, password: string): Promise<Sesion> {
  const respuesta = await pedir("/auth/sesion", { email, password });

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  const datos = (await respuesta.json()) as RespuestaDeSesion;
  const sesion = { acceso: datos.access, refresco: datos.refresh, usuario: datos.usuario };
  guardarSesion(sesion);
  return sesion;
}

export type DatosDeRegistro = {
  nombre: string;
  email: string;
  password: string;
  rut?: string;
};

/**
 * Crea una cuenta de comprador y la deja con sesión iniciada.
 *
 * El rol no se manda: lo fija el backend. Mandarlo no serviría de nada.
 */
export async function registrarComprador(datos: DatosDeRegistro): Promise<Sesion> {
  const respuesta = await pedir("/auth/registro", datos);

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return iniciarSesion(datos.email, datos.password);
}

export function cerrarSesion() {
  borrarSesion();
}

/** Pide un token de acceso nuevo. Devuelve si lo consiguió. */
async function renovar(): Promise<boolean> {
  const refresco = instantanea()?.refresco;
  if (!refresco) {
    return false;
  }

  const respuesta = await pedir("/auth/sesion/renovar", { refresh: refresco });
  if (!respuesta.ok) {
    return false;
  }

  const { access } = (await respuesta.json()) as { access: string };
  guardarAcceso(access);
  return true;
}

/**
 * Llama a la API con el token de la sesión.
 *
 * Si el token venció, lo renueva una vez y repite la llamada. Si tampoco sirve
 * el de refresco, borra la sesión: seguir con credenciales muertas solo
 * produce errores más adelante.
 */
export async function pedirConSesion(ruta: string, opciones: RequestInit = {}): Promise<Response> {
  const llamar = async () => {
    const acceso = instantanea()?.acceso;

    try {
      return await fetch(`${API}${ruta}`, {
        ...opciones,
        headers: {
          "Content-Type": "application/json",
          ...(acceso ? { Authorization: `Bearer ${acceso}` } : {}),
          ...opciones.headers,
        },
      });
    } catch {
      throw errorDeConexion();
    }
  };

  const respuesta = await llamar();
  if (respuesta.status !== 401) {
    return respuesta;
  }

  if (!(await renovar())) {
    borrarSesion();
    return respuesta;
  }

  return llamar();
}
