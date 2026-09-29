import type { Metadata } from "next";
import { Cormorant_Garamond, Inter, Manrope, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

// Tipografías del mockup: Cormorant Garamond para títulos y precios, Manrope
// para todo lo demás. next/font las sirve desde el propio sitio, sin pedirle
// nada a Google desde el navegador del comprador.
const cormorant = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  display: "swap",
});

// Tipografías de la portada de DealCommerce, que es otra marca: Plus Jakarta
// para los títulos e Inter para el texto. Se sirven desde el propio sitio por
// lo mismo que las anteriores.
const inter = Inter({
  variable: "--fuente-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

const jakarta = Plus_Jakarta_Sans({
  variable: "--fuente-jakarta",
  subsets: ["latin"],
  weight: ["600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "DealCommerce",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es-CL"
      className={`${cormorant.variable} ${manrope.variable} ${inter.variable} ${jakarta.variable} dark h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
