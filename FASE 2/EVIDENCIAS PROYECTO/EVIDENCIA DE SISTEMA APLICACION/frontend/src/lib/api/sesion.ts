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

/**
 * Falta el segundo paso: la cuenta tiene la verificación en dos pasos activa.
 * Con el desafío y el código de la app, `verificarCodigo` termina de entrar.
 */
export type DesafioDeDosPasos = { otpRequerido: true; desafio: string };

export function esDesafio(valor: Sesion | DesafioDeDosPasos): valor is DesafioDeDosPasos {
  return "otpRequerido" in valor;
}

function guardarRespuesta(datos: RespuestaDeSesion): Sesion {
  const sesion = { acceso: datos.access, refresco: datos.refresh, usuario: datos.usuario };
  guardarSesion(sesion);
  return sesion;
}

/**
 * Entra con correo y contraseña, y deja la sesión guardada.
 *
 * Si la cuenta tiene la verificación en dos pasos activa, todavía no hay
 * sesión: devuelve el desafío para pedir el código.
 */
export async function iniciarSesion(email: string, password: string): Promise<Sesion | DesafioDeDosPasos> {
  const respuesta = await pedir("/auth/sesion", { email, password });

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  const datos = (await respuesta.json()) as RespuestaDeSesion | DesafioDeDosPasos;
  if ("otpRequerido" in datos) return datos;
  return guardarRespuesta(datos);
}

/** El segundo paso: el código de la app (o uno de respaldo) a cambio de la sesión. */
export async function verificarCodigo(desafio: string, codigo: string): Promise<Sesion> {
  const respuesta = await pedir("/auth/sesion/otp", { desafio, codigo });
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }
  return guardarRespuesta((await respuesta.json()) as RespuestaDeSesion);
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

  // Un comprador nunca tiene verificación en dos pasos: la respuesta es la sesión.
  return (await iniciarSesion(datos.email, datos.password)) as Sesion;
}

/**
 * Pide el enlace para crear una contraseña nueva.
 *
 * La respuesta es la misma exista o no la cuenta: el backend no revela quién
 * está registrado. `tienda` hace que el enlace vuelva a esa tienda.
 */
export async function pedirEnlaceDeContrasena(email: string, tienda?: string): Promise<string> {
  const respuesta = await pedir("/auth/contrasena/olvido", { email, tienda: tienda ?? "" });
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }
  return ((await respuesta.json()) as { detalle: string }).detalle;
}

/** Crea la contraseña nueva con el enlace del correo. Devuelve el correo de la cuenta. */
export async function restablecerContrasena(uid: string, token: string, password: string): Promise<string> {
  const respuesta = await pedir("/auth/contrasena/restablecer", { uid, token, password });
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }
  return ((await respuesta.json()) as { email: string }).email;
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

    // Un cuerpo multipart escribe su propio Content-Type, con la frontera que
    // separa las partes. Ponerlo a mano la deja fuera y el servidor no puede
    // leer el archivo.
    const esFormulario = opciones.body instanceof FormData;

    try {
      return await fetch(`${API}${ruta}`, {
        ...opciones,
        headers: {
          ...(esFormulario ? {} : { "Content-Type": "application/json" }),
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
