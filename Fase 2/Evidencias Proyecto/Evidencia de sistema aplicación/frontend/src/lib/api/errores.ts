/*
 * Errores de la API.
 *
 * El backend responde siempre con la misma forma
 * (CLAUDE.md > Errores y respuestas de la API):
 *
 *   {"error": {"codigo": "...", "mensaje": "...", "detalles": {"campo": [...]}}}
 *
 * `mensaje` ya viene redactado en español para mostrárselo a la persona, así
 * que el frontend no reescribe textos de error: los ubica.
 */

/** Errores por campo. Siempre lista, aunque sea uno solo. */
export type DetallesDeError = Record<string, string[]>;

export class ErrorDeApi extends Error {
  readonly codigo: string;
  readonly detalles: DetallesDeError;

  constructor(codigo: string, mensaje: string, detalles: DetallesDeError = {}) {
    super(mensaje);
    this.name = "ErrorDeApi";
    this.codigo = codigo;
    this.detalles = detalles;
  }

  /** El error de un campo, si el backend lo marcó. */
  de(campo: string): string | null {
    return this.detalles[campo]?.[0] ?? null;
  }
}

const SIN_RESPUESTA = new ErrorDeApi(
  "sin_conexion",
  "No pudimos comunicarnos con el servidor. Revisa tu conexión y vuelve a probar.",
);

export function errorDeConexion(): ErrorDeApi {
  return SIN_RESPUESTA;
}

/**
 * Convierte una respuesta fallida en un error con mensaje mostrable.
 *
 * Una respuesta que no trae el formato esperado (un 502 del proxy, por ejemplo)
 * no debe romper la pantalla con un error de JSON.
 */
export async function leerError(respuesta: Response): Promise<ErrorDeApi> {
  try {
    const cuerpo = await respuesta.json();
    const error = cuerpo?.error;

    if (error?.mensaje) {
      return new ErrorDeApi(error.codigo ?? "error", error.mensaje, error.detalles ?? {});
    }
  } catch {
    // Sigue de largo al mensaje genérico.
  }

  return new ErrorDeApi("error", "No pudimos completar la operación. Vuelve a probar.");
}
