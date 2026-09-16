import type { ContenidoTienda } from "@/lib/tipos";

/**
 * Contenido de la tienda pública de Joyas Ye.
 *
 * PROVISORIO. Todos los textos vienen tal cual del mockup "Joyas Ye - Tienda"
 * y todavía no están validados con el cliente. Cuando exista la API, este
 * contenido lo entrega el backend desde el modelo Tienda y este archivo se borra.
 *
 * Para usar el logo real:
 *   1. Copiar el archivo a  frontend/public/tiendas/joyas-ye/  (p. ej. logo.svg).
 *   2. Completar `logo` abajo con su ruta y medidas en píxeles.
 * Mientras `logo` sea null se muestra la marca dibujada en el mockup.
 */
export const joyasYe: ContenidoTienda = {
  slug: "joyas-ye",
  nombre: "Joyas Ye",

  // Ejemplo: { src: "/tiendas/joyas-ye/logo.svg", ancho: 120, alto: 32, incluyeNombre: true }
  // `incluyeNombre: true` si el archivo ya trae escrito "Joyas Ye" y no hay que
  // repetir el nombre en texto al lado.
  logo: null,

  // Enlaces completos, empezando en https:// (por ejemplo
  // "https://wa.me/56912345678"). Sin número ni cuenta confirmados, los botones
  // y los íconos de redes se muestran igual pero quedan inertes.
  redes: {
    whatsapp: null,
    instagram: null,
  },

  buscador: {
    placeholder: "Buscar joyas…",
  },

  portada: {
    titulo: "Piezas que se heredan, no que se reemplazan",
    garantias: ["Envíos a todo Chile"],
    movil: {
      titulo: "Piezas que se heredan",
    },
  },

  llamadoMayorista: {
    titulo: "¿Compras para tu tienda?",
    boton: "Solicitar cuenta mayorista",
    movil: {
      boton: "Solicitar cuenta",
    },
  },

  pie: {
    columnas: [
      {
        titulo: "Comprar",
        enlaces: ["Anillos", "Collares", "Aros", "Pulseras", "Precios por volumen"],
      },
      {
        titulo: "Ayuda",
        enlaces: ["Envíos", "Cambios y devoluciones", "Contacto", "Guía de tallas"],
      },
      {
        titulo: "Nosotros",
        enlaces: ["Nuestra historia", "El taller", "Cuidado de tus joyas"],
      },
    ],
    escribenos: {
      titulo: "Escríbenos",
      boton: "Escríbenos por WhatsApp",
    },
    derechos: "© 2026 Joyas Ye. Todos los derechos reservados.",
    movil: {
      columnas: [
        { titulo: "Comprar", enlaces: ["Anillos", "Collares", "Aros", "Pulseras"] },
        { titulo: "Ayuda", enlaces: ["Envíos", "Cambios", "Contacto", "Nosotros"] },
      ],
      derechos: "© 2026 Joyas Ye · Todos los derechos reservados",
    },
  },
};
