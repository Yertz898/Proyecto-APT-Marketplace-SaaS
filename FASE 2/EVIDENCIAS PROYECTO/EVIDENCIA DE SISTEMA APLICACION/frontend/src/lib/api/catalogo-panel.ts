import { leerError } from "@/lib/api/errores";
import { pedirConSesion } from "@/lib/api/sesion";
import type { FormaVenta, UnidadMedida } from "@/lib/tipos";
import type {
  CategoriaDelPanel,
  PaginaDelPanel,
  ProductoDelPanel,
  ResumenDeInventario,
} from "@/lib/tipos-panel";

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

// ── Escribir ────────────────────────────────────────────────────────────────

/**
 * Lo que se manda al crear o editar. Todo opcional al editar: solo lo que cambió.
 *
 * Va siempre multipart porque la foto es un archivo, y mezclar dos formas de
 * enviar según lo que cambió duplicaría el camino por nada.
 */
export type CambiosDelProducto = Partial<{
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: string;
  formaVenta: FormaVenta;
  unidadMedida: UnidadMedida;
  precioNeto: number;
  controlaStock: boolean;
  stock: number | null;
  cantidadMinima: number;
  cantidadPiezas: number | null;
  activo: boolean;
  foto: File;
}>;

function comoFormulario(cambios: CambiosDelProducto): FormData {
  const cuerpo = new FormData();
  for (const [campo, valor] of Object.entries(cambios)) {
    if (valor === undefined) continue;
    // Un null explícito sí se manda: es "no lleva inventario", que no es lo
    // mismo que "no toqué este campo".
    cuerpo.append(campo, valor === null ? "" : (valor as string | Blob));
  }
  return cuerpo;
}

export async function crearProducto(
  cambios: CambiosDelProducto,
): Promise<ProductoDelPanel> {
  const respuesta = await pedirConSesion("/panel/productos", {
    method: "POST",
    body: comoFormulario(cambios),
  });

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as ProductoDelPanel;
}

export async function editarProducto(
  codigo: string,
  cambios: CambiosDelProducto,
): Promise<ProductoDelPanel> {
  const respuesta = await pedirConSesion(
    `/panel/productos/${encodeURIComponent(codigo)}`,
    { method: "PATCH", body: comoFormulario(cambios) },
  );

  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as ProductoDelPanel;
}

export async function obtenerCategorias(): Promise<CategoriaDelPanel[]> {
  const respuesta = await pedirConSesion("/panel/categorias");
  if (!respuesta.ok) {
    throw await leerError(respuesta);
  }

  return (await respuesta.json()) as CategoriaDelPanel[];
}
