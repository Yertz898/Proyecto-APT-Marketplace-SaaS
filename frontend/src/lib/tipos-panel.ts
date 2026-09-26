/**
 * Tipos del panel de la tienda.
 *
 * Separados de los tipos de la tienda pública a propósito: son dos aplicaciones
 * distintas y no deben compartir componentes ni modelos (prompt de actualización
 * del frontend).
 */

/** Cada tipo de carga tiene su plantilla, su validación y su pantalla. */
export type TipoCarga = "lotes" | "granel" | "fotos";

export type LimitesCarga = {
  /** Extensiones que acepta el backend, p. ej. [".xlsx", ".csv"]. */
  extensiones: string[];
  tamanoMaximoBytes: number;
};

export type FilaRechazada = {
  fila: number;
  /** Motivo en español, redactado por el backend. Se muestra como texto, nunca como HTML. */
  motivo: string;
};

/**
 * Resultado de validar una planilla SIN aplicarla.
 *
 * `ausentes` son los códigos que hoy existen en la tienda y no vienen en el
 * archivo. No se borran: solo se desactivan si el dueño lo pide explícitamente
 * al confirmar.
 */
export type ResumenCarga = {
  cargaId: string;
  crear: number;
  actualizar: number;
  rechazar: number;
  rechazos: FilaRechazada[];
  ausentes: string[];
};

/** Resultado de emparejar el .zip de fotos con los lotes ya cargados. */
export type ResumenFotos = {
  cargaId: string;
  emparejadas: number;
  lotesSinFoto: string[];
  fotosSinLote: string[];
};

export type CargaHistorial = {
  id: string;
  tipo: TipoCarga;
  /** Fecha en ISO; se formatea a dd-mm-aaaa al mostrarla. */
  fecha: string;
  usuario: string;
  archivo: string;
  /** Texto de resultado redactado por el backend. */
  resultado: string;
};
