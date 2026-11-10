import type { CSSProperties } from "react";

import { esHexadecimal, paletaParaFondoClaro } from "@/lib/color";
import type { Paleta } from "@/lib/color";
import type { ColoresTienda } from "@/lib/tipos";

/*
 * Identidad visual de la tienda.
 *
 * Los colores del vendedor entran al diseño solo como variables CSS y solo si
 * son hexadecimales válidos. Nunca se inserta CSS ni HTML escrito por él: todas
 * las tiendas comparten origen, así que un script inyectado en una podría leer
 * la sesión de los compradores de otra.
 *
 * Las variables van con nombre propio (`--tienda-*`) y no pisan directamente
 * los tokens del diseño. Quien decide qué token toma cuál es la hoja de
 * estilos, según el tema que el comprador tenga puesto: el mismo color de marca
 * necesita un acento claro sobre el fondo negro y uno oscuro sobre el crema, o
 * en uno de los dos no se lee.
 */

/** La paleta de la plataforma, para la tienda que todavía no eligió la suya. */
const PLATAFORMA: Paleta = {
  primario: "#7c3aed",
  hover: "#8b5cf6",
  acento: "#a78bfa",
  destacado: "#c9a227",
};

const valido = (color: string | undefined) =>
  typeof color === "string" && esHexadecimal(color) ? color : null;

/**
 * Convierte los colores de la tienda en variables CSS para aplicar con `style`.
 * Un color mal formado se ignora y queda el de la plataforma.
 */
export function variablesDeIdentidad(colores: ColoresTienda | null): CSSProperties {
  const oscura: Paleta = {
    primario: valido(colores?.primario) ?? PLATAFORMA.primario,
    hover: valido(colores?.primarioHover) ?? PLATAFORMA.hover,
    acento: valido(colores?.acento) ?? PLATAFORMA.acento,
    destacado: valido(colores?.destacado) ?? PLATAFORMA.destacado,
  };

  const clara = paletaParaFondoClaro(oscura);

  return {
    "--tienda-primario": oscura.primario,
    "--tienda-primario-hover": oscura.hover,
    "--tienda-acento": oscura.acento,
    "--tienda-destacado": oscura.destacado,

    "--tienda-primario-hover-claro": clara.hover,
    "--tienda-acento-claro": clara.acento,
    "--tienda-destacado-claro": clara.destacado,
  } as CSSProperties;
}
