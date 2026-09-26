/**
 * Tipos de la tienda pública.
 *
 * Todo lo que distingue a una tienda de otra son datos que entrega el backend:
 * su identidad, sus categorías, sus lotes y sus líneas de granel. Nada de eso se
 * escribe en el frontend. Si mañana entra una segunda tienda con otras
 * categorías y otras líneas, este archivo no cambia.
 */

/** Pesos chilenos enteros, sin decimales. Los precios se manejan NETOS. */
export type Pesos = number;

export type Imagen = {
  url: string;
  alt: string;
};

// ── Identidad de la tienda ──────────────────────────────────────────────────

/**
 * Colores de la tienda, en hexadecimal.
 *
 * Se aplican como variables CSS y se validan antes de usarse. Nunca se renderiza
 * HTML ni CSS escrito por el vendedor: todas las tiendas comparten origen, y un
 * script inyectado en una leería la sesión de los compradores de otra.
 */
export type ColoresTienda = {
  primario: string;
  primarioHover: string;
  acento: string;
  destacado: string;
};

export type IdentidadTienda = {
  slug: string;
  nombre: string;
  logo: Imagen | null;
  banner: Imagen | null;
  colores: ColoresTienda | null;
  redes: {
    whatsapp: string | null;
    instagram: string | null;
  };
};

// ── Productos ───────────────────────────────────────────────────────────────

/**
 * Tipos de producto de la plataforma.
 *
 * Los componentes discriminan por este campo. Sumar un tercer tipo (una tienda
 * que venda piezas sueltas, por ejemplo) debe ser agregar un caso, no reescribir.
 */
export type TipoProducto = "lote" | "granel";

export type PiezasPorCategoria = {
  categoria: string;
  cantidad: number;
};

/** UNICO no se repite; MULTIPLE se repite y lleva la cuenta de lo que queda. */
export type Cupos = { tipo: "UNICO" } | { tipo: "MULTIPLE"; restantes: number };

/**
 * Lote: unidad de venta cerrada.
 *
 * Es una composición (cuántas piezas de cada categoría), no una lista de piezas
 * concretas: los modelos varían según disponibilidad. Se compra entero, sin
 * seleccionar nada.
 *
 * El backend entrega neto, IVA y total ya calculados: el navegador no hace
 * aritmética de dinero.
 */
export type Lote = {
  tipo: "lote";
  codigo: string;
  nombre: string;
  material: string;
  piezasTotales: number;
  composicion: PiezasPorCategoria[];
  precioNeto: Pesos;
  iva: Pesos;
  precioTotal: Pesos;
  cupos: Cupos;
  agotado: boolean;
  /** Null mientras el dueño no haya subido la foto: no se dibuja nada en su lugar. */
  foto: Imagen | null;
};

export type UnidadUmbral = "pesos" | "gramos";

/**
 * Tramo de una línea de granel.
 *
 * El umbral puede venir en pesos o en gramos, y `unidadUmbral` dice cuál es. Se
 * muestran tal como los definió la tienda, sin convertir entre unidades.
 */
export type TramoGranel = {
  umbral: number;
  unidadUmbral: UnidadUmbral;
  precioGramoNeto: Pesos;
};

/** Granel: venta por gramo, organizada en líneas con sus tramos. */
export type LineaGranel = {
  tipo: "granel";
  codigo: string;
  nombre: string;
  material: string;
  categorias: string[];
  tramos: TramoGranel[];
  /** Mínimo de compra, redactado por el backend. Null si la línea no tiene. */
  minimo: string | null;
};

export type ItemCatalogo = Lote | LineaGranel;

/**
 * Cotización de una compra por gramos.
 *
 * La calcula siempre el backend. El frontend puede resaltar el tramo para
 * orientar, pero el total que se cobra no se calcula en el navegador.
 */
export type CotizacionGranel = {
  gramos: number;
  precioGramoNeto: Pesos;
  neto: Pesos;
  iva: Pesos;
  total: Pesos;
  /** Índice del tramo aplicado dentro de `LineaGranel.tramos`; null si no aplica ninguno. */
  tramoAplicado: number | null;
  /** Aviso de conveniencia cuando comprar más cuesta menos. Lo decide el backend. */
  aviso: string | null;
  /** Motivo por el que no se puede comprar (bajo el mínimo). Si viene, no se agrega al carrito. */
  rechazo: string | null;
};

// ── Listados ────────────────────────────────────────────────────────────────

export type PaginaDeLotes = {
  lotes: Lote[];
  paginaActual: number;
  totalPaginas: number;
};

// ── Carrito y pedido ────────────────────────────────────────────────────────

/**
 * Lo que el comprador eligió: solo referencias y cantidades.
 *
 * Ningún precio se guarda acá. Los tramos de lotes dependen de cuántos lotes
 * lleva el pedido completo, así que cotizar es siempre trabajo del backend.
 */
export type LineaCarrito =
  | { tipo: "lote"; codigo: string; cantidad: number }
  | { tipo: "granel"; codigo: string; gramos: number };

export type LineaCotizada = {
  linea: LineaCarrito;
  nombre: string;
  /** Cantidad con su unidad, ya redactada por el backend: "3 lotes", "166,5 g". */
  detalle: string;
  neto: Pesos;
  iva: Pesos;
  total: Pesos;
  /** Motivo por el que esta línea no se puede comprar (cupo agotado, bajo el mínimo). */
  rechazo: string | null;
};

export type CarritoCotizado = {
  lineas: LineaCotizada[];
  neto: Pesos;
  iva: Pesos;
  total: Pesos;
  /** Cuánto falta para el siguiente tramo por cantidad de lotes. Lo redacta el backend. */
  avisoTramo: string | null;
  /** Si viene, el pedido no se puede confirmar todavía. */
  rechazo: string | null;
};

export type PedidoConfirmado = {
  numero: string;
  mensaje: string;
  /** Enlace para coordinar el pago; el checkout es simulado. */
  enlaceWhatsapp: string | null;
};
