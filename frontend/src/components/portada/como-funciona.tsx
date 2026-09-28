import { TituloDeSeccion } from "./secciones";

/*
 * Los tres pasos para tener la tienda andando.
 *
 * Va en una lista ordenada de verdad: el orden es parte del contenido, no de la
 * presentación. Los números grandes son decorativos y el marcador propio de la
 * lista se quita.
 */

const PASOS = [
  {
    titulo: "Sube tu catálogo desde Excel",
    detalle: "Usa la planilla que ya tienes. Ordenamos tus productos, fotos y tramos de precio.",
  },
  {
    titulo: "Dale tu estilo",
    detalle: "Elige colores, logo y tipografía. Tu tienda se ve como tu marca, no como la nuestra.",
  },
  {
    titulo: "Comparte el enlace y recibe pedidos",
    detalle:
      "Pégalo en tu bio de Instagram o mándalo por WhatsApp. Los pedidos llegan con el total calculado.",
  },
];

export function ComoFunciona() {
  return (
    <section id="como-funciona" className="px-[clamp(20px,5.5cqi,80px)] py-[clamp(64px,7cqi,112px)]">
      <div className="mx-auto flex max-w-[1280px] flex-col gap-[clamp(32px,3.5cqi,56px)]">
        <TituloDeSeccion antetitulo="Cómo funciona">Tu tienda lista en tres pasos</TituloDeSeccion>

        <ol className="grid list-none grid-cols-[repeat(auto-fit,minmax(min(100%,300px),1fr))] gap-[clamp(24px,3cqi,40px)] p-0">
          {PASOS.map((paso, posicion) => (
            <li key={paso.titulo} className="flex flex-col gap-3.5 border-t-2 border-marino pt-6">
              <span
                aria-hidden="true"
                className="font-jakarta text-[44px] leading-none font-extrabold tracking-[-0.03em] text-acero"
              >
                {String(posicion + 1).padStart(2, "0")}
              </span>
              <h3 className="font-jakarta text-[22px] leading-[1.25] font-bold">{paso.titulo}</h3>
              <p className="text-base leading-[1.55] text-pizarra text-pretty">{paso.detalle}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
