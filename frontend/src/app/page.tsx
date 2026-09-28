import type { Metadata } from "next";

import { Pie, Preguntas, Privacidad } from "@/components/portada/cierre";
import { ComoFunciona } from "@/components/portada/como-funciona";
import { Encabezado } from "@/components/portada/encabezado";
import { Funciones } from "@/components/portada/funciones";
import { Hero } from "@/components/portada/hero";
import { PanelDeVentas } from "@/components/portada/panel-ventas";
import { Planes } from "@/components/portada/planes";
import { Problema } from "@/components/portada/problema";
import { TiendaDeEjemplo } from "@/components/portada/tienda-ejemplo";

export const metadata: Metadata = {
  title: "DealCommerce · Tu catálogo mayorista en línea",
  description:
    "Deja de cotizar por WhatsApp. Tu catálogo mayorista en línea, con precios por volumen que se calculan solos.",
};

/*
 * Portada de DealCommerce.
 *
 * Es la única parte del sitio que le habla al vendedor antes de que sea
 * cliente. No comparte nada con la vitrina de una tienda: otra paleta, otras
 * tipografías y otro tono, porque la vitrina se ve como la tienda quiera y esto
 * se ve como la plataforma.
 *
 * El contenedor de arriba declara `container-type: inline-size` y todas las
 * medidas elásticas de adentro van en unidades `cqi`, no `vw`. Así la página se
 * mide contra el ancho del contenedor y no contra el de la ventana, que es lo
 * que permitía verla en el diseño a 1440 y a 390 sin dos hojas de estilo.
 */
export default function Portada() {
  return (
    <div data-tema="claro" className="@container min-h-dvh w-full bg-hueso font-inter text-marino">
      <Encabezado />
      <Hero />
      <Problema />
      <ComoFunciona />
      <Funciones />
      <TiendaDeEjemplo />
      <PanelDeVentas />
      <Planes />
      <Privacidad />
      <Preguntas />
      <Pie />
    </div>
  );
}
