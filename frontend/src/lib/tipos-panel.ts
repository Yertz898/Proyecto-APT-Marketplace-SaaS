/**
 * Tipos del panel de la tienda.
 *
 * Separados de los tipos de la tienda pública a propósito: son dos aplicaciones
 * distintas y no deben compartir componentes ni modelos.
 */

import type { Imagen, Plan } from "@/lib/tipos";

/** Cada tipo de carga tiene su plantilla, su validación y su pantalla. */
export type TipoCarga = "productos" | "tramos" | "fotos";

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

/** Resultado de emparejar el .zip de fotos con los productos ya cargados. */
export type ResumenFotos = {
  cargaId: string;
  emparejadas: number;
  productosSinFoto: string[];
  fotosSinProducto: string[];
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

// ── Perfil de la tienda ─────────────────────────────────────────────────────

/**
 * Una tipografía de la lista cerrada que mantiene el backend.
 *
 * La lista viaja con el perfil en vez de estar escrita acá: todas las tiendas
 * comparten origen, así que la fuente no la elige el vendedor escribiéndola,
 * sino eligiéndola de lo que el backend permite.
 */
export type TipografiaDisponible = {
  valor: string;
  nombre: string;
};

/** El perfil tal como lo entrega GET /panel/tienda. */
export type PerfilDeTienda = {
  slug: string;
  nombre: string;
  plan: Plan;
  logoActual: Imagen | null;
  bannerActual: Imagen | null;
  colorPrimario: string;
  colorPrimarioHover: string;
  colorAcento: string;
  colorDestacado: string;
  tipografia: string;
  whatsapp: string;
  instagram: string;
  tipografiasDisponibles: TipografiaDisponible[];
  /** Lo decide el plan, y lo decide el backend. El candado de la interfaz solo lo refleja. */
  puedeEditarLaMarca: boolean;
};

/** Lo que se manda en un PATCH. Todo opcional: se envía solo lo que cambió. */
export type CambiosDelPerfil = Partial<{
  nombre: string;
  colorPrimario: string;
  colorPrimarioHover: string;
  colorAcento: string;
  colorDestacado: string;
  tipografia: string;
  whatsapp: string;
  instagram: string;
  logo: File;
  banner: File;
}>;
