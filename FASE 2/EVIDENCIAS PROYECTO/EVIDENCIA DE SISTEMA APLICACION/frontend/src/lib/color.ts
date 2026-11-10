/*
 * Aritmética de color de la marca.
 *
 * Está acá y no dentro de la pantalla porque son funciones puras y porque dos
 * cosas distintas las usan: el selector, para dibujar la rueda, y el formulario,
 * para armar los cuatro colores que exige el contrato.
 *
 * El backend sigue recibiendo cuatro hexadecimales. Lo que cambia es quién los
 * escribe: antes el dueño de la tienda, ahora `derivarPaleta`.
 */

/** Tono (0-360), intensidad (0-100) y brillo (0-100). */
export type Hsv = { h: number; s: number; v: number };

/** Los cuatro colores del perfil, en el orden en que se muestran. */
export type Paleta = {
  primario: string;
  hover: string;
  acento: string;
  destacado: string;
};

/** El mismo formato que exige el backend: seis dígitos y nada más. */
export function esHexadecimal(valor: string): boolean {
  return /^#[0-9a-fA-F]{6}$/.test(valor);
}

export function aHex({ h, s, v }: Hsv): string {
  const croma = (v / 100) * (s / 100);
  const segundo = croma * (1 - Math.abs(((h / 60) % 2) - 1));
  const base = v / 100 - croma;

  const tramos: [number, number, number][] = [
    [croma, segundo, 0],
    [segundo, croma, 0],
    [0, croma, segundo],
    [0, segundo, croma],
    [segundo, 0, croma],
    [croma, 0, segundo],
  ];
  const canales = tramos[Math.min(Math.floor(h / 60), 5)];

  const aPar = (canal: number) =>
    Math.round((canal + base) * 255)
      .toString(16)
      .padStart(2, "0");

  return `#${canales.map(aPar).join("")}`.toUpperCase();
}

export function aHsv(hex: string): Hsv {
  const [r, g, b] = [1, 3, 5].map((inicio) => parseInt(hex.slice(inicio, inicio + 2), 16) / 255);
  const alto = Math.max(r, g, b);
  const recorrido = alto - Math.min(r, g, b);

  let h = 0;
  if (recorrido !== 0) {
    if (alto === r) h = 60 * (((g - b) / recorrido) % 6);
    else if (alto === g) h = 60 * ((b - r) / recorrido + 2);
    else h = 60 * ((r - g) / recorrido + 4);
  }

  // Sin redondear: `aHsv(aHex(x))` tiene que devolver el mismo color. Con dos
  // decimales de menos, abrir el selector y cerrarlo movía el color del dueño.
  return {
    h: (h + 360) % 360,
    s: alto === 0 ? 0 : (recorrido / alto) * 100,
    v: alto * 100,
  };
}

const acotar = (valor: number, minimo: number, maximo: number) =>
  Math.round(Math.min(Math.max(valor, minimo), maximo));

/** Los dos fondos de la vitrina. Lo que se dibuje encima tiene que leerse. */
export const FONDO_OSCURO = "#0B0A0F";
export const FONDO_CLARO = "#F7F5F0";

/**
 * Aclara un color hasta que se lea sobre un fondo oscuro.
 *
 * Primero sube el brillo y, si con el brillo al tope todavía no alcanza, baja
 * la intensidad. Un rojo saturado es oscuro por mucho brillo que se le ponga:
 * aporta apenas un quinto de la luminancia que aporta un verde, así que la
 * única salida es desteñirlo hacia el rosa.
 */
function aclararHasta(hsv: Hsv, fondo: string, minimo: number): Hsv {
  let actual = hsv;

  while (contraste(aHex(actual), fondo) < minimo && (actual.v < 100 || actual.s > 20)) {
    actual =
      actual.v < 100
        ? { ...actual, v: Math.min(actual.v + 2, 100) }
        : { ...actual, s: Math.max(actual.s - 2, 20) };
  }

  return actual;
}

/**
 * Oscurece un color hasta que se lea sobre un fondo claro.
 *
 * Es el espejo del anterior: baja el brillo y, si tocando fondo todavía no
 * alcanza, sube la intensidad, que en los tonos oscuros ayuda a separarse del
 * papel. El tono no se toca nunca: es el color que eligió el dueño.
 */
function oscurecerHasta(hsv: Hsv, fondo: string, minimo: number): Hsv {
  let actual = hsv;

  while (contraste(aHex(actual), fondo) < minimo && (actual.v > 8 || actual.s < 100)) {
    actual =
      actual.v > 8
        ? { ...actual, v: Math.max(actual.v - 2, 8) }
        : { ...actual, s: Math.min(actual.s + 2, 100) };
  }

  return actual;
}

/**
 * Los otros tres colores a partir del primero.
 *
 * El dueño elige uno solo y de ahí salen los demás. La regla la dicta la
 * vitrina, que es de tema oscuro: `acento` y `destacado` terminan como texto
 * sobre fondo casi negro, así que van más claros que el primario, no más
 * oscuros. El `hover` también aclara, porque sobre fondo oscuro un botón que se
 * apaga al pasar el mouse parece desactivado.
 *
 * Las proporciones salen de la paleta de la plataforma, que ya resolvió el
 * problema a mano: de #7C3AED nacen #8B5CF6, #A78BFA y #C9A227.
 *
 * El `destacado` cruza al otro lado de la rueda porque una oferta tiene que
 * saltar contra el resto y no confundirse con un botón.
 */
export function derivarPaleta({ h, s, v }: Hsv): Paleta {
  return {
    primario: aHex({ h, s, v }),
    hover: aHex({ h, s: acotar(s * 0.83, 0, 100), v: acotar(v * 1.04, 0, 100) }),
    acento: aHex(
      aclararHasta(
        { h, s: acotar(s * 0.59, 18, 100), v: acotar(Math.max(v * 1.06, 88), 0, 100) },
        FONDO_OSCURO,
        4.5,
      ),
    ),
    destacado: aHex(
      aclararHasta(
        { h: (h + 150) % 360, s: acotar(s, 65, 85), v: acotar(Math.max(v, 78), 0, 92) },
        FONDO_OSCURO,
        4.5,
      ),
    ),
  };
}

/**
 * La misma paleta, llevada al fondo claro.
 *
 * `acento` y `destacado` son texto, y la de arriba los dejó claros para que se
 * leyeran sobre el negro: sobre crema desaparecen. Acá se oscurecen conservando
 * el tono, que es lo que el dueño eligió. El `hover` cambia de sentido: sobre
 * fondo claro un botón se oscurece al pasar el mouse, no se aclara.
 *
 * El primario no se toca. Es el fondo del botón y lleva texto blanco en los dos
 * temas, así que vale lo mismo en ambos.
 */
export function paletaParaFondoClaro({ primario, acento, destacado }: Paleta): Paleta {
  const base = aHsv(primario);

  return {
    primario,
    hover: aHex({ h: base.h, s: acotar(base.s * 1.05, 0, 100), v: acotar(base.v * 0.84, 8, 100) }),
    acento: aHex(oscurecerHasta(aHsv(acento), FONDO_CLARO, 4.5)),
    destacado: aHex(oscurecerHasta(aHsv(destacado), FONDO_CLARO, 4.5)),
  };
}

/** Luminancia relativa, como la define WCAG 2.1. */
function luminancia(hex: string): number {
  const canales = [1, 3, 5].map((inicio) => {
    const canal = parseInt(hex.slice(inicio, inicio + 2), 16) / 255;
    return canal <= 0.03928 ? canal / 12.92 : ((canal + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * canales[0] + 0.7152 * canales[1] + 0.0722 * canales[2];
}

/** Razón de contraste entre dos colores: de 1 (iguales) a 21 (blanco y negro). */
export function contraste(uno: string, otro: string): number {
  const [mayor, menor] = [luminancia(uno) + 0.05, luminancia(otro) + 0.05].sort((a, b) => b - a);
  return mayor / menor;
}
