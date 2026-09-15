/**
 * Tipos de datos de la tienda pública.
 *
 * Reflejan lo que muestra el mockup y el modelo de dominio del CONVENCIONES.md. Cuando
 * exista la API se ajustan al contrato real de los endpoints; hasta entonces son
 * la referencia de qué necesita recibir cada pantalla.
 */

/** Pesos chilenos, enteros y con IVA incluido (CONVENCIONES.md > Moneda y números). */
export type Pesos = number;

// ── Contenido de la tienda ──────────────────────────────────────────────────

export type Logo = {
  src: string;
  ancho: number;
  alto: number;
  /** true si la imagen ya contiene el nombre escrito de la tienda. */
  incluyeNombre: boolean;
};

export type ColumnaPie = {
  titulo: string;
  enlaces: string[];
};

export type ContenidoTienda = {
  slug: string;
  nombre: string;
  logo: Logo | null;
  redes: {
    whatsapp: string | null;
    instagram: string | null;
  };
  buscador: {
    placeholder: string;
  };
  portada: {
    antetitulo: string;
    titulo: string;
    descripcion: string;
    garantias: string[];
    movil: {
      antetitulo: string;
      titulo: string;
      descripcion: string;
    };
  };
  llamadoMayorista: {
    titulo: string;
    descripcion: string;
    boton: string;
    movil: {
      descripcion: string;
      boton: string;
    };
  };
  pie: {
    descripcion: string;
    columnas: ColumnaPie[];
    escribenos: {
      titulo: string;
      texto: string;
      boton: string;
    };
    derechos: string;
    movil: {
      descripcion: string;
      columnas: ColumnaPie[];
      derechos: string;
    };
  };
};

// ── Catálogo ────────────────────────────────────────────────────────────────

export type Imagen = {
  url: string;
  alt: string;
};

export type Categoria = {
  slug: string;
  nombre: string;
  cantidadProductos: number;
};

export type ProductoResumen = {
  slug: string;
  nombre: string;
  /** Línea bajo el nombre en la tarjeta, p. ej. "Plata 925 · 4 tallas". */
  resumen: string;
  precioDetalle: Pesos;
  /** Cantidad desde la que aplica el primer tramo mayorista; null si no tiene. */
  cantidadMinimaMayorista: number | null;
  imagen: Imagen | null;
};

export type FiltrosCatalogo = {
  categorias: Categoria[];
  materiales: string[];
  precioMinimo: Pesos | null;
  precioMaximo: Pesos | null;
  cantidadMinimaMayorista: number | null;
};

export type PaginaCatalogo = {
  productos: ProductoResumen[];
  total: number;
  totalConMayorista: number;
  paginaActual: number;
  totalPaginas: number;
  filtros: FiltrosCatalogo;
};

// ── Ficha de producto ───────────────────────────────────────────────────────

export type TramoPrecio = {
  /** El tramo aplica desde esta cantidad (CONVENCIONES.md > Tramos de precio). */
  cantidadMinima: number;
  precioUnitario: Pesos;
  /** Texto de la etiqueta, p. ej. "Detalle", "Mayorista", "Mayorista +". */
  etiqueta: string;
};

/** El stock vive en la variante, no en el producto. */
export type Variante = {
  sku: string;
  material: string;
  talla: string;
  stock: number;
};

export type Caracteristica = {
  nombre: string;
  valor: string;
};

export type ProductoDetalle = {
  slug: string;
  nombre: string;
  categoria: Pick<Categoria, "slug" | "nombre">;
  coleccion: string | null;
  descripcion: string;
  caracteristicas: Caracteristica[];
  imagenes: Imagen[];
  materiales: string[];
  tallas: string[];
  variantes: Variante[];
  /**
   * Tramos que el comprador actual puede ver. Qué tramos se incluyen lo decide
   * el backend según la aprobación mayorista: es una regla de autorización, el
   * frontend no oculta nada por su cuenta.
   */
  tramos: TramoPrecio[];
};
