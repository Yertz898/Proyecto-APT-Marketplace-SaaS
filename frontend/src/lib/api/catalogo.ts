import type {
  Categoria,
  PaginaCatalogo,
  ProductoDetalle,
  ProductoResumen,
} from "@/lib/tipos";

/*
 * Acceso a los datos del catálogo público.
 *
 * Todavía no existe la API, así que estas funciones devuelven vacío: las
 * pantallas se construyen contra la forma final de los datos y, al conectar el
 * backend, solo cambia el cuerpo de cada función.
 *
 * Al implementarlas (CONVENCIONES.md):
 * - La tienda va en la ruta (/t/<slug>/...) y la API solo expone datos publicados.
 * - Los tramos mayoristas los filtra el backend según el comprador autenticado.
 * - Los listados vienen paginados, con tope de página.
 */

export async function obtenerCategorias(slugTienda: string): Promise<Categoria[]> {
  void slugTienda;
  return [];
}

export async function obtenerMasPedidos(slugTienda: string): Promise<ProductoResumen[]> {
  void slugTienda;
  return [];
}

export async function obtenerCatalogo(
  slugTienda: string,
  pagina: number,
): Promise<PaginaCatalogo> {
  void slugTienda;
  return {
    productos: [],
    total: 0,
    totalConMayorista: 0,
    paginaActual: pagina,
    totalPaginas: 0,
    filtros: {
      categorias: [],
      materiales: [],
      precioMinimo: null,
      precioMaximo: null,
      cantidadMinimaMayorista: null,
    },
  };
}

export async function obtenerProducto(
  slugTienda: string,
  slugProducto: string,
): Promise<ProductoDetalle | null> {
  void slugTienda;
  void slugProducto;
  return null;
}
