import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

// Las cuatro familias viven en el repositorio, en src/fuentes. Antes se pedían
// a Google en tiempo de compilación con next/font/google, y eso dejaba el build
// a merced de un servicio externo: en octubre de 2026 Google cambió el formato
// de entrega de una de ellas y la aplicación dejó de compilar sin que nadie
// hubiera tocado una línea. Un archivo versionado no se puede mover solo.
//
// Son las cuatro variables, así que cada familia es un archivo único que cubre
// todo el rango de pesos. Se sirven desde el propio sitio, sin pedirle nada a
// Google desde el navegador del comprador.
//
// El `unicode-range` repetido es el subconjunto latino, el único que traen los
// archivos y el mismo que pedía `subsets: ["latin"]`. Declararlo deja que el
// navegador recurra a la fuente de reserva si aparece un carácter fuera del
// rango, en vez de dibujar un cuadro vacío. Va escrito entero en cada llamada
// porque el cargador de fuentes se evalúa al compilar y no acepta variables.

// Tipografías del mockup: Cormorant Garamond para títulos y precios, Manrope
// para todo lo demás.
const cormorant = localFont({
  src: "../fuentes/cormorant-garamond-variable.woff2",
  variable: "--font-cormorant",
  weight: "400 700",
  display: "swap",
  adjustFontFallback: "Times New Roman",
  declarations: [
    {
      prop: "unicode-range",
      value:
        "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
    },
  ],
});

const manrope = localFont({
  src: "../fuentes/manrope-variable.woff2",
  variable: "--font-manrope",
  weight: "200 800",
  display: "swap",
  declarations: [
    {
      prop: "unicode-range",
      value:
        "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
    },
  ],
});

// Tipografías de la portada de DealCommerce, que es otra marca: Plus Jakarta
// para los títulos e Inter para el texto.
const inter = localFont({
  src: "../fuentes/inter-variable.woff2",
  variable: "--fuente-inter",
  weight: "400 600",
  display: "swap",
  declarations: [
    {
      prop: "unicode-range",
      value:
        "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
    },
  ],
});

const jakarta = localFont({
  src: "../fuentes/plus-jakarta-sans-variable.woff2",
  variable: "--fuente-jakarta",
  weight: "600 800",
  display: "swap",
  declarations: [
    {
      prop: "unicode-range",
      value:
        "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
    },
  ],
});

export const metadata: Metadata = {
  title: "DealCommerce",
};

/*
 * `suppressHydrationWarning` va solo por el tema de la vitrina: un guion le
 * pone `data-vitrina` a esta etiqueta antes de que React hidrate, para que
 * quien eligió el tema claro no vea un golpe de negro al cargar. React mira el
 * HTML del servidor, que todavía no lo tenía, y avisa de una diferencia que es
 * a propósito. La supresión es de un solo nivel: alcanza a los atributos de
 * este <html> y a nada más abajo.
 */
export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es-CL"
      suppressHydrationWarning
      className={`${cormorant.variable} ${manrope.variable} ${inter.variable} ${jakarta.variable} dark h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
