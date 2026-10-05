/*
 * Destinos de la portada, en un solo lugar.
 *
 * Están acá y no repartidos por las secciones porque varios se repiten: el
 * botón de solicitar acceso aparece cinco veces y el de la tienda de ejemplo,
 * dos.
 */

/** Formulario para pedir entrar a la plataforma. */
export const SOLICITAR_ACCESO = "/solicitar-acceso";

/**
 * Entrada del vendedor.
 *
 * Va al panel y no a la vitrina porque esta página le habla al dueño de una
 * tienda mayorista, no a quien compra.
 */
export const ENTRAR = "/panel/entrar";

/**
 * Tienda que la portada muestra como ejemplo.
 *
 * Sale de una variable de entorno y no del código: ninguna tienda en
 * particular puede quedar escrita acá, y cambiar cuál se muestra no debería
 * ser un despliegue. Sin la variable, el botón lleva al formulario de
 * solicitud, que es la acción que la portada quiere de todos modos.
 */
const SLUG_DE_EJEMPLO = process.env.NEXT_PUBLIC_TIENDA_DE_EJEMPLO;

export const TIENDA_DE_EJEMPLO = SLUG_DE_EJEMPLO
  ? `/t/${SLUG_DE_EJEMPLO}`
  : "#solicitar";

/** Las tres secciones que enlaza el menú. */
export const SECCIONES = [
  { href: "#como-funciona", etiqueta: "Cómo funciona" },
  { href: "#funciones", etiqueta: "Funciones" },
  { href: "#planes", etiqueta: "Planes" },
];
