import Link from "next/link";

import { TIENDA_DE_EJEMPLO } from "./enlaces";

/*
 * La sección que demuestra el argumento central del producto: la plataforma es
 * una, las tiendas se ven distintas.
 *
 * Los morados de la maqueta van escritos a mano y no como tokens del tema a
 * propósito. Son la paleta de una tienda inventada, no de DealCommerce; meterlos
 * en el tema sugeriría que la plataforma tiene un morado, y justamente no lo
 * tiene: el color lo pone cada tienda.
 */

const PRODUCTOS = [
  { nombre: "Rubor compacto", precio: "$4.990", figura: "size-[40%] rounded-full bg-[#7C3AED]" },
  { nombre: "Máscara de pestañas", precio: "$6.490", figura: "h-[56%] w-[22%] rounded-[4px] bg-[#A78BFA]" },
  { nombre: "Paleta de sombras", precio: "$12.990", figura: "h-[30%] w-[46%] rounded-[6px] bg-[#5B21B6]" },
];

export function TiendaDeEjemplo() {
  return (
    <section id="ejemplo" className="px-[clamp(20px,5.5cqi,80px)] py-[clamp(64px,7cqi,112px)]">
      <div className="mx-auto grid max-w-[1280px] grid-cols-[repeat(auto-fit,minmax(min(100%,420px),1fr))] items-center gap-[clamp(36px,5cqi,72px)] rounded-[24px] bg-marino p-[clamp(28px,5cqi,72px)]">
        <div className="flex flex-col items-start gap-[18px]">
          <span className="rounded-[6px] bg-ambar px-2.5 py-[5px] text-xs font-bold tracking-[0.06em] text-marino uppercase">
            Tienda de ejemplo
          </span>

          <h2 className="font-jakarta text-[clamp(30px,3.3cqi,46px)] leading-[1.08] font-extrabold tracking-[-0.03em] text-white text-balance">
            Cada tienda tiene su propia identidad
          </h2>

          <p className="max-w-[28em] text-[17px] leading-[1.55] text-[#D5DBE5] text-pretty">
            DealCommerce es claro y ordenado por dentro. Tu tienda, por fuera, se ve como tú quieras: esta es
            oscura, con morado, y vende cosmética al por mayor.
          </p>

          <Link
            href={TIENDA_DE_EJEMPLO}
            className="mt-2 inline-flex h-[52px] items-center gap-2 rounded-[12px] bg-white px-6 text-base font-semibold text-marino no-underline hover:bg-cielo hover:no-underline"
          >
            Ver una tienda de ejemplo <span aria-hidden="true">→</span>
          </Link>
        </div>

        <MaquetaNoctambula />
      </div>
    </section>
  );
}

/** Vitrina inventada, con una paleta deliberadamente distinta a la de la portada. */
function MaquetaNoctambula() {
  return (
    <div
      aria-hidden="true"
      className="overflow-hidden rounded-[16px] border border-[#2A2238] bg-[#0B0A10] shadow-[0_24px_60px_rgba(0,0,0,.35)]"
    >
      <div className="flex items-center justify-between border-b border-[#221B2E] px-[18px] py-3.5">
        <span className="font-jakarta text-base font-extrabold tracking-[0.14em] text-white">NOCTÁMBULA</span>
        <span className="text-[11px] text-[#C4B5FD]">Catálogo · Pedido</span>
      </div>

      <div className="flex flex-col gap-4 p-[18px]">
        <div className="flex items-center justify-between gap-3 rounded-[12px] bg-[#1A1426] p-5">
          <div className="flex flex-col gap-1.5">
            <span className="text-[10px] tracking-[0.1em] text-[#C4B5FD] uppercase">Nueva colección</span>
            <span className="font-jakarta text-xl leading-[1.1] font-extrabold text-white">
              Labiales al por mayor
            </span>
            <span className="mt-1.5 self-start rounded-full bg-[#7C3AED] px-3 py-1.5 text-[11px] font-semibold text-white">
              Ver productos
            </span>
          </div>
          <div className="flex h-[72px] flex-none items-end gap-2">
            <div className="h-[60%] w-3.5 rounded-t-[7px] rounded-b-[2px] bg-[#A78BFA]" />
            <div className="h-[90%] w-3.5 rounded-t-[7px] rounded-b-[2px] bg-[#7C3AED]" />
            <div className="h-[72%] w-3.5 rounded-t-[7px] rounded-b-[2px] bg-[#5B21B6]" />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2.5">
          {PRODUCTOS.map((producto) => (
            <div key={producto.nombre} className="flex flex-col gap-1.5">
              <div className="flex aspect-square items-center justify-center rounded-[10px] bg-[#1A1426]">
                <div className={producto.figura} />
              </div>
              <span className="text-[11px] text-[#E9E3F5]">{producto.nombre}</span>
              <span className="text-xs font-bold text-white">{producto.precio}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
