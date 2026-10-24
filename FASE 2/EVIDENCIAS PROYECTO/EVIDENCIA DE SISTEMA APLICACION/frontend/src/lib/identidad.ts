import type { CSSProperties } from "react";

import type { ColoresTienda } from "@/lib/tipos";

/*
 * Identidad visual de la tienda.
 *
 * Los colores del vendedor entran al diseño solo como variables CSS y solo si
 * son hexadecimales válidos. Nunca se inserta CSS ni HTML escrito por él: todas
 * las tiendas comparten origen, así que un script inyectado en una podría leer
 * la sesión de los compradores de otra.
 */

const HEXADECIMAL = /^#[0-9a-fA-F]{6}$/;

/** Variables que la tienda puede cambiar. El resto de la paleta es de la plataforma. */
const VARIABLES: Record<keyof ColoresTienda, string> = {
  primario: "--color-violeta",
  primarioHover: "--color-violeta-hover",
  acento: "--color-lila",
  destacado: "--color-oro",
};

/**
 * Convierte los colores de la tienda en variables CSS para aplicar con `style`.
 * Un color mal formado se ignora y queda el de la plataforma.
 */
export function variablesDeIdentidad(colores: ColoresTienda | null): CSSProperties {
  if (!colores) {
    return {};
  }

  const variables: Record<string, string> = {};
  for (const [clave, variable] of Object.entries(VARIABLES)) {
    const color = colores[clave as keyof ColoresTienda];
    if (typeof color === "string" && HEXADECIMAL.test(color)) {
      variables[variable] = color;
    }
  }

  return variables as CSSProperties;
}
