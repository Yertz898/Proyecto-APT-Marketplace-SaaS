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
 * Tienda que se muestra como ejemplo.
 *
 * Es el único lugar del frontend donde el nombre de una tienda está escrito en
 * el código, por decisión del equipo. En el resto del sistema la tienda sale
 * siempre de la ruta o de la sesión; cambiar de tienda de ejemplo es cambiar
 * esta línea.
 */
export const TIENDA_DE_EJEMPLO = "/t/joyas-ye";

/** Las tres secciones que enlaza el menú. */
export const SECCIONES = [
  { href: "#como-funciona", etiqueta: "Cómo funciona" },
  { href: "#funciones", etiqueta: "Funciones" },
  { href: "#planes", etiqueta: "Planes" },
];
