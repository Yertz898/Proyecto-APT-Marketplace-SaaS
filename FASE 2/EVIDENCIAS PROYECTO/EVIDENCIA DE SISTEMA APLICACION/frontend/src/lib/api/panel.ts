import { leerError } from "@/lib/api/errores";
import { pedirConSesion } from "@/lib/api/sesion";
import type {
  CargaHistorial,
  LimitesCarga,
  ResumenCarga,
  ResumenFotos,
  TipoCarga,
} from "@/lib/tipos-panel";

/*
 * Carga masiva del catálogo.
 *
 * El recorrido tiene tres pasos y el orden importa: **validar, mirar,
 * confirmar**. Validar no escribe una sola fila; lo que devuelve es lo que
 * pasaría. El catálogo se toca recién al confirmar, con el resumen ya a la
 * vista.
 *
 * Quien valida de verdad es el backend, y lo hace por el contenido del archivo
 * y no por su extensión. Lo que revisa el frontend antes de subir es cortesía:
 * evitarle a la persona una espera para un error que se ve de entrada.
 */

const LIMITES_DESCONOCIDOS = null;

async function pedir(ruta: string, opciones?: RequestInit): Promise<Response> {
  const respuesta = await pedirConSesion(ruta, opciones);
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }
  return respuesta;
}

export async function obtenerLimitesDeCarga(): Promise<LimitesCarga | null> {
  try {
    return (await (await pedir("/panel/cargas/limites")).json()) as LimitesCarga;
  } catch {
    // Sin límites conocidos la pantalla omite ese aviso, en vez de mostrar un
    // número inventado.
    return LIMITES_DESCONOCIDOS;
  }
}

/**
 * La plantilla se descarga con la sesión puesta, así que no sirve un enlace
 * directo: se pide, se arma un objeto temporal y se suelta.
 */
export async function descargarPlantilla(tipo: TipoCarga): Promise<void> {
  const respuesta = await pedir(`/panel/plantillas/${tipo}`);
  const contenido = await respuesta.blob();

  const url = URL.createObjectURL(contenido);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = `plantilla-${tipo}.xlsx`;
  enlace.click();
  URL.revokeObjectURL(url);
}

function conArchivo(archivo: File): RequestInit {
  const cuerpo = new FormData();
  cuerpo.append("archivo", archivo);
  return { method: "POST", body: cuerpo };
}

export async function validarCarga(tipo: TipoCarga, archivo: File): Promise<ResumenCarga> {
  const respuesta = await pedir(`/panel/cargas/${tipo}/validar`, conArchivo(archivo));
  return (await respuesta.json()) as ResumenCarga;
}

export async function validarFotos(archivo: File): Promise<ResumenFotos> {
  const respuesta = await pedir("/panel/cargas/fotos/validar", conArchivo(archivo));
  return (await respuesta.json()) as ResumenFotos;
}

export async function confirmarCarga(
  cargaId: string,
  desactivarAusentes: boolean,
): Promise<void> {
  await pedir(`/panel/cargas/${cargaId}/confirmar`, {
    method: "POST",
    body: JSON.stringify({ desactivarAusentes }),
  });
}

export async function cancelarCarga(cargaId: string): Promise<void> {
  await pedir(`/panel/cargas/${cargaId}`, { method: "DELETE" });
}

export async function obtenerHistorialDeCargas(
  tipo?: TipoCarga,
): Promise<CargaHistorial[]> {
  const consulta = tipo ? `?tipo=${tipo}` : "";
  try {
    return (await (await pedir(`/panel/cargas${consulta}`)).json()) as CargaHistorial[];
  } catch {
    // El historial es contexto, no el contenido de la pantalla: si falla, la
    // carga sigue funcionando.
    return [];
  }
}
