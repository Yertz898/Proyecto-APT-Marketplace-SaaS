/**
 * Tipos del panel de la tienda.
 *
 * Separados de los tipos de la tienda pública a propósito: son dos aplicaciones
 * distintas y no deben compartir componentes ni modelos.
 */

import type { FormaVenta, Imagen, Pesos, Plan, UnidadMedida } from "@/lib/tipos";

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
  /**
   * Imágenes que el backend no pudo usar: archivos que no son imagen, o un
   * nombre que más de un producto reclama. Van aparte de `fotosSinProducto`
   * porque esas sí se entendieron, solo que no le tocaban a nadie.
   */
  rechazos: FilaRechazada[];
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

// ── Catálogo desde el panel ─────────────────────────────────────────────────

/**
 * En una palabra, qué le pasa a un producto.
 *
 * Son hechos, no predicciones. La alerta por demanda proyectada necesita el
 * pronóstico y todavía no existe.
 */
export type EstadoDeProducto = "publicado" | "ultima" | "agotado" | "desactivado";

/**
 * Un producto como lo lista y lo edita el panel.
 *
 * Trae todo lo editable y no un resumen: si faltara la descripción o las
 * piezas, el formulario las abriría vacías y guardarlas las borraría.
 */
export type ProductoDelPanel = {
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: string | null;
  formaVenta: FormaVenta;
  unidadMedida: UnidadMedida;
  precioNeto: number;
  controlaStock: boolean;
  /** Null cuando la tienda no lleva inventario de este producto. */
  stock: number | null;
  cantidadMinima: number;
  /** Solo en la venta por lote. */
  cantidadPiezas: number | null;
  /** Cuántos tramos de precio tiene. */
  tramos: number;
  activo: boolean;
  estado: EstadoDeProducto;
  /** Null cuando no hay: la pantalla no dibuja un marcador en su lugar. */
  foto: Imagen | null;
};

export type PaginaDelPanel = {
  productos: ProductoDelPanel[];
  paginaActual: number;
  totalPaginas: number;
};

export type ResumenDeInventario = {
  publicados: number;
  desactivados: number;
  agotados: number;
  ultimaUnidad: number;
};

/** Una categoría de la tienda, con cuántos productos la usan. */
export type CategoriaDelPanel = {
  id: number;
  nombre: string;
  productos: number;
};

// ── Pedidos ─────────────────────────────────────────────────────────────────

/**
 * Los cuatro estados por los que pasa un pedido.
 *
 * `CANCELADO` no es un estado más: anular devuelve el inventario reservado,
 * así que es la única transición que toca el catálogo.
 */
export type EstadoPedido = "PENDIENTE" | "CONFIRMADO" | "ENTREGADO" | "CANCELADO";

export type LineaDelPedido = {
  id: number;
  productoNombre: string;
  productoCodigo: string;
  /** Viene como texto decimal del backend: "2.00", "166.50". */
  cantidad: string;
  precioUnitarioNeto: Pesos;
  subtotalNeto: Pesos;
  subtotalIva: Pesos;
  subtotalTotal: Pesos;
};

/**
 * Un pedido como lo ve el dueño.
 *
 * Los precios son los del momento en que se confirmó, no los del catálogo de
 * hoy: cambiar un precio no puede reescribir lo que ya se cobró.
 */
export type PedidoDelPanel = {
  id: number;
  folio: string;
  estado: EstadoPedido;
  estadoVisible: string;
  nombreContacto: string;
  telefonoContacto: string;
  emailContacto: string;
  direccionEntrega: string;
  notas: string;
  totalNeto: Pesos;
  totalIva: Pesos;
  total: Pesos;
  /** Fecha en ISO. */
  creadoEn: string;
  lineas: LineaDelPedido[];
};

// ── Ventas ──────────────────────────────────────────────────────────────────

export type CifrasDeVentas = {
  pedidos: number;
  neto: Pesos;
  iva: Pesos;
  total: Pesos;
};

export type ProductoMasVendido = {
  codigo: string;
  nombre: string;
  neto: Pesos;
  /** Suma de las cantidades vendidas, como decimal: "10.00", "650.00". */
  cantidad: string;
};

export type ProductoDetenido = {
  codigo: string;
  nombre: string;
  precioNeto: Pesos;
  /** Días desde su última venta, o null si no se vendió nunca. */
  diasSinVender: number | null;
  /** Fecha aaaa-mm-dd en que entró al catálogo. */
  enCatalogoDesde: string;
};

/**
 * Lo que la tienda vendió. Son hechos sumados de pedidos, no estimaciones.
 *
 * Un pedido pendiente no cuenta como venta —el pago se coordina fuera de la
 * plataforma— y va aparte en `porCoordinar`. Uno anulado no cuenta nunca.
 */
export type ResumenDeVentas = {
  mes: { etiqueta: string; desde: string };
  ventas: CifrasDeVentas;
  /** `variacion` es null si el mes anterior no tuvo ventas: no hay con qué comparar. */
  mesAnterior: CifrasDeVentas & { variacion: number | null };
  porCoordinar: { pedidos: number; total: Pesos };
  /**
   * Los últimos doce meses, para el gráfico. Los meses sin ventas vienen en
   * cero: omitirlos uniría octubre con diciembre como si fueran seguidos.
   */
  serieMensual: {
    mes: string;
    etiqueta: string;
    pedidos: number;
    total: Pesos;
    /** El mes en curso. Va por la mitad, así que su cifra no es comparable. */
    enCurso: boolean;
  }[];
  /** Sobre cuántos días se miran los más vendidos y los detenidos. */
  diasDeVentana: number;
  masVendidos: ProductoMasVendido[];
  sinMovimiento: ProductoDetenido[];
};

// ── Pronóstico y segmentos ──────────────────────────────────────────────────

/**
 * Lo que se espera vender de un producto el próximo mes.
 *
 * `suficiente` manda sobre todo lo demás: cuando es falso no hay proyección,
 * hay un producto del que todavía no se puede decir nada. La pantalla tiene
 * que decir eso y no un cero.
 */
export type ProyeccionDeProducto = {
  codigo: string;
  nombre: string;
  unidad: UnidadMedida;
  mesesConVentas: number;
  suficiente: boolean;
  esperado: number | null;
  /** Con qué se calculó: hoy siempre la línea base. Null si no se proyectó. */
  metodo: string | null;
  stock: number | null;
  /** Días hasta quedarse sin stock al ritmo proyectado. Null si no aplica. */
  diasHastaQuiebre: number | null;
  serie: { mes: string; cantidad: number }[];
};

export type PronosticoDeDemanda = {
  /** Cuántos meses de ventas necesita un producto para que se lo proyecte. */
  minimoDeMeses: number;
  productos: ProyeccionDeProducto[];
};

export type NombreDeSegmento = "habitual" | "nuevo" | "en_riesgo" | "perdido";

export type CompradorSegmentado = {
  nombre: string;
  segmento: NombreDeSegmento;
  /** Días desde su última compra. */
  recencia: number;
  frecuencia: number;
  monto: Pesos;
};

export type SegmentacionDeCompradores = {
  metodo: string;
  /** Días sin volver a partir de los cuales se considera que alguien se fue. */
  umbralDeDias: number;
  /** Si el umbral salió de los datos de la tienda o es el valor por omisión. */
  umbralCalculado: boolean;
  descripciones: Record<NombreDeSegmento, string>;
  conteo: Record<NombreDeSegmento, number>;
  clientes: CompradorSegmentado[];
};

// ── Asistente ───────────────────────────────────────────────────────────────

/**
 * Lo que el asistente sabe contestar.
 *
 * Se pide a la API en vez de escribirse en el frontend: si las dos listas se
 * separaran, la pantalla ofrecería preguntas que el backend ya no responde.
 */
export type PreguntasDelAsistente = {
  preguntas: { intencion: string; texto: string }[];
  largoMaximo: number;
};

export type RespuestaDelAsistente = {
  intencion: string;
  texto: string;
  /** A qué sección del panel lleva el detalle, si corresponde. */
  seccion: string | null;
  /**
   * Quién entendió la pregunta. El texto sale siempre de la base: esto solo
   * dice si eligió la respuesta el modelo o la tabla de palabras clave.
   */
  clasificadoPor: "modelo" | "palabras clave";
};
