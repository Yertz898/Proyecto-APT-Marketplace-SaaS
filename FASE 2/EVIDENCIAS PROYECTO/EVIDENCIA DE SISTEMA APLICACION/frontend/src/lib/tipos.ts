/**
 * Tipos de la tienda pública.
 *
 * Todo lo que distingue a una tienda de otra son datos que entrega el backend:
 * su identidad, sus categorías y sus productos. Nada de eso se escribe en el
 * frontend. Si mañana entra una tienda que vende de otra manera, este archivo
 * no cambia.
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

// ── Sesión ──────────────────────────────────────────────────────────────────

/** Los cuatro roles del sistema, y no hay más (CONVENCIONES.md > Roles). */
export type Rol = "admin_plataforma" | "dueno_tienda" | "vendedor" | "comprador";

/** Niveles de suscripción. Deciden qué secciones del panel se habilitan. */
export type Plan = "basico" | "premium" | "ultimate";

export type TiendaDeLaSesion = {
  slug: string;
  nombre: string;
  plan: Plan;
};

/**
 * Quién inició sesión.
 *
 * Sirve para decidir qué dibujar, nunca qué se puede hacer: eso lo resuelve el
 * backend en cada endpoint. Esconder un botón no protege nada.
 */
export type UsuarioSesion = {
  id: number;
  nombre: string;
  email: string;
  rol: Rol;
  /** El rol escrito para mostrar: "Dueño de tienda". */
  rolNombre: string;
  /** Null para el comprador y el administrador: no pertenecen a una tienda. */
  tienda: TiendaDeLaSesion | null;
};

// ── Productos ───────────────────────────────────────────────────────────────

/**
 * Cómo vende la tienda cada producto.
 *
 * Es lo único que distingue a una tienda de ropa de una joyería que vende por
 * gramo: la forma de venta es un dato del producto, no una rama del código.
 */
export type FormaVenta = "unidad" | "lote" | "peso";

/** En qué se mide. La vitrina la muestra tal cual, sin convertir. */
export type UnidadMedida = "unidad" | "g" | "kg";

/** Una forma de venta con su nombre, tal como la entrega el backend. */
export type FormaDeVenta = {
  valor: FormaVenta;
  nombre: string;
};

export type PiezasPorCategoria = {
  categoria: string;
  cantidad: number;
};

/**
 * Qué se le puede decir al comprador sobre las existencias.
 *
 * Son cuatro situaciones distintas y el backend ya decidió cuál es: la tienda
 * no lleva inventario de esto, queda una sola, quedan varias, o se acabó. La
 * última unidad va aparte porque empuja a decidir.
 */
export type Disponibilidad =
  | { tipo: "sin_control" }
  | { tipo: "agotado" }
  | { tipo: "ultima" }
  | { tipo: "disponible"; restantes: number };

export type UnidadUmbral = "cantidad" | "monto" | "peso";

/**
 * Un escalón de precio: desde tal umbral, este precio por unidad de medida.
 *
 * El umbral puede venir en cantidad, en monto o en peso, y `unidadUmbral` dice
 * cuál es. No hay descuentos: el valor es siempre un precio.
 */
export type TramoPrecio = {
  umbral: number;
  unidadUmbral: UnidadUmbral;
  precioNeto: Pesos;
};

/**
 * Lo que una tienda vende.
 *
 * Un solo tipo para las tres formas de venta. Lo que no aplica a una forma
 * viene en `null` o vacío, nunca en otra forma: así la vitrina tiene un tipo y
 * no tres, y una tienda que mañana venda de otra manera no obliga a tocar esto.
 *
 * El backend entrega neto, IVA y total ya calculados: el navegador no hace
 * aritmética de dinero.
 */
export type Producto = {
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: string | null;
  formaVenta: FormaVenta;
  unidadMedida: UnidadMedida;
  precioNeto: Pesos;
  iva: Pesos;
  precioTotal: Pesos;
  disponibilidad: Disponibilidad;
  agotado: boolean;
  cantidadMinima: number;
  /** Solo en la venta por lote: contra esto cuadra la composición. */
  piezasTotales: number | null;
  composicion: PiezasPorCategoria[];
  tramos: TramoPrecio[];
  /** Mínimo de compra por monto, redactado por el backend. Null si no tiene. */
  minimo: string | null;
  /** Null mientras el dueño no haya subido la foto: no se dibuja nada en su lugar. */
  foto: Imagen | null;
};

/**
 * Cotización de una cantidad.
 *
 * La calcula siempre el backend. El frontend puede resaltar el tramo para
 * orientar, pero el total que se cobra no se calcula en el navegador.
 *
 * `rechazo` y el precio son excluyentes. `motivo` distingue los dos rechazos
 * que se confunden: no llegar al mínimo por monto no es lo mismo que pedir
 * menos que la cantidad mínima del producto.
 */
export type Cotizacion = {
  cantidad: number;
  precioUnitario: Pesos;
  neto: Pesos;
  iva: Pesos;
  total: Pesos;
  /** Umbral del tramo aplicado; null si se cobró el precio base. */
  tramoAplicado: number | null;
  unidadTramo: UnidadUmbral | null;
  /** Aviso de conveniencia cuando comprar más cuesta menos. Lo decide el backend. */
  aviso: string | null;
  rechazo: string | null;
  motivo: string | null;
};

// ── Listados ────────────────────────────────────────────────────────────────

export type PaginaDeProductos = {
  productos: Producto[];
  paginaActual: number;
  totalPaginas: number;
};

// ── Carrito y pedido ────────────────────────────────────────────────────────

/**
 * Lo que el comprador eligió: solo referencias y cantidades.
 *
 * Una sola forma, en la unidad de medida del producto. Ningún precio se guarda
 * acá: el precio depende del tramo que alcance el pedido completo, así que
 * cotizar es siempre trabajo del backend.
 */
export type LineaCarrito = {
  codigo: string;
  cantidad: number;
};

export type LineaCotizada = {
  linea: LineaCarrito;
  nombre: string;
  /** Cantidad con su unidad, ya redactada por el backend: "3", "166,5 g". */
  detalle: string;
  neto: Pesos;
  iva: Pesos;
  total: Pesos;
  /** Motivo por el que esta línea no se puede comprar (sin stock, bajo el mínimo). */
  rechazo: string | null;
};

export type CarritoCotizado = {
  lineas: LineaCotizada[];
  neto: Pesos;
  iva: Pesos;
  total: Pesos;
  /** Cuánto falta para el siguiente tramo. Lo redacta el backend. */
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

// ── Agenda de visitas ───────────────────────────────────────────────────────

export type HoraDisponible = {
  /** Instante en ISO; se muestra siempre en hora de Chile. */
  inicio: string;
  fin: string;
  bloqueId: number;
  nombreBloque: string;
  cuposLibres: number;
  confirmacionAutomatica: boolean;
};

/** Rango de días, en fechas aaaa-mm-dd. */
export type RangoDeDias = {
  desde: string;
  hasta: string;
};

export type EstadoVisita =
  | "solicitada"
  | "confirmada"
  | "asistida"
  | "no_asistio"
  | "rechazada"
  | "cancelada";

/** Una visita ya pedida, como la ve el comprador. */
export type Visita = {
  uid: string;
  inicio: string;
  fin: string;
  estado: EstadoVisita;
  /** El estado escrito para mostrar: "Solicitada". */
  estadoNombre: string;
  nombreContacto: string;
  correoContacto: string;
  telefonoContacto: string;
  motivo: string;
};

export type SolicitudDeVisita = {
  inicio: string;
  nombreContacto: string;
  correoContacto: string;
  telefonoContacto: string;
  motivo?: string;
};

export type AgendaPublica = {
  direccion: string;
  indicaciones: string;
  anticipacionMinimaHoras: number;
  /** Todo lo que la tienda acepta: los límites hasta donde se puede navegar. */
  ventana: RangoDeDias;
  /** El pedazo que trae esta respuesta. Las horas son solo de estos días. */
  rango: RangoDeDias;
  horas: HoraDisponible[];
};
