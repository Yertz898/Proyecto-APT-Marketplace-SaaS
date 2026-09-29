import type { LimitesCarga, TipoCarga } from "@/lib/tipos-panel";

/**
 * Configuración de cada tipo de carga.
 *
 * Agregar un tipo nuevo es agregar una entrada acá, no escribir otra pantalla:
 * la ruta /panel/cargas/[tipo] se arma con estos datos.
 *
 * Las columnas son las de la plantilla que entrega el backend. Se muestran para
 * que el dueño sepa qué esperar antes de descargarla.
 */
export const TIPOS_DE_CARGA = {
  lotes: {
    titulo: "Catálogo de lotes",
    descripcion: "Un lote por fila. Si el código ya existe, la fila lo actualiza; si no, lo crea.",
    columnas: [
      "codigo",
      "nombre",
      "precio_neto",
      "cupos",
      "tipo_cupo",
      "material",
      "piezas_por_categoria",
      "foto",
    ],
    extensiones: [".xlsx", ".csv"],
  },
  granel: {
    titulo: "Líneas de granel",
    descripcion:
      "Una fila por tramo. El umbral puede ir en pesos o en gramos, y la columna unidad_umbral dice cuál es.",
    columnas: ["codigo_linea", "nombre", "material", "umbral", "unidad_umbral", "precio_gramo_neto"],
    extensiones: [".xlsx", ".csv"],
  },
  fotos: {
    titulo: "Fotos de productos",
    descripcion:
      "Un .zip o .rar con las imágenes. Se emparejan con los lotes por el nombre de archivo de la columna foto.",
    columnas: [],
    extensiones: [".zip", ".rar"],
  },
} as const satisfies Record<
  TipoCarga,
  { titulo: string; descripcion: string; columnas: readonly string[]; extensiones: readonly string[] }
>;

export function esTipoDeCarga(valor: string): valor is TipoCarga {
  return valor in TIPOS_DE_CARGA;
}

/**
 * Formatos de planilla que se rechazan, con la explicación de cómo guardarlos
 * bien. Se avisa antes de subir, no después de fallar.
 */
const FORMATOS_RECHAZADOS: Record<string, string> = {
  ".xls": "El formato .xls es antiguo. Abre el archivo en Excel y usa Archivo → Guardar como → Libro de Excel (.xlsx).",
  ".xlsm": "El formato .xlsm contiene macros y no se acepta. Guárdalo como Libro de Excel (.xlsx), sin macros.",
};

export type RevisionArchivo = { ok: true } | { ok: false; mensaje: string };

function extensionDe(nombre: string): string {
  const punto = nombre.lastIndexOf(".");
  return punto === -1 ? "" : nombre.slice(punto).toLowerCase();
}

export function formatearTamano(bytes: number): string {
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(mb < 10 ? 1 : 0).replace(".", ",")} MB`;
}

/**
 * Revisión del archivo en el navegador.
 *
 * Es ayuda para el usuario, no un control de seguridad: el control real lo hace
 * el backend, que valida por contenido y no por extensión.
 */
export function revisarArchivo(
  archivo: File,
  extensionesAceptadas: readonly string[],
  limites: LimitesCarga | null,
): RevisionArchivo {
  const extension = extensionDe(archivo.name);

  const explicacion = FORMATOS_RECHAZADOS[extension];
  if (explicacion) {
    return { ok: false, mensaje: explicacion };
  }

  if (!extensionesAceptadas.includes(extension)) {
    return {
      ok: false,
      mensaje: `Este tipo de carga acepta ${extensionesAceptadas.join(" o ")}. El archivo que elegiste es ${extension || "de tipo desconocido"}.`,
    };
  }

  if (limites && archivo.size > limites.tamanoMaximoBytes) {
    return {
      ok: false,
      mensaje: `El archivo pesa ${formatearTamano(archivo.size)} y el máximo es ${formatearTamano(limites.tamanoMaximoBytes)}.`,
    };
  }

  return { ok: true };
}
