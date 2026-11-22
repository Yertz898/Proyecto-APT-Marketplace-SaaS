import Link from "next/link";

import { NOMBRE_DE_EJEMPLO, TIENDA_DE_EJEMPLO } from "./enlaces";

/*
 * La sección que demuestra el argumento central del producto: la plataforma es
 * una, las tiendas se ven distintas.
 *
 * La maqueta imita la vitrina de la tienda a la que lleva el botón: oscura, con
 * acento violeta y títulos con serifa. Antes mostraba una tienda inventada con
 * otro nombre, y el botón llevaba a otra: se notaba. El nombre sale de la misma
 * variable de entorno que el enlace, así que los dos no se pueden separar.
 *
 * Los colores van escritos a mano y no como tokens del tema a propósito: son
 * la paleta de una tienda, no de DealCommerce.
 */

const PRODUCTOS = [
  { nombre: "Cadena de plata 925", detalle: "Por gramo", precio: "$1.290 / g" },
  { nombre: "Lote de pulseras", detalle: "Por lote", precio: "$20.000" },
  { nombre: "Aros argolla", detalle: "Por unidad", precio: "$6.490" },
];

export function TiendaDeEjemplo() {
  return (
    <section id="ejemplo" className="px-[clamp(20px,5.5cqi,80px)] py-[clamp(64px,7cqi,112px)]">
      <div className="mx-auto grid max-w-[1280px] grid-cols-[repeat(auto-fit,minmax(min(100%,420px),1fr))] items-center gap-[clamp(36px,5cqi,72px)] rounded-2xl bg-marino p-[clamp(28px,5cqi,72px)]">
        <div className="flex flex-col items-start gap-[18px]">
          <span className="rounded-[6px] bg-ambar px-2.5 py-[5px] text-xs font-bold tracking-[0.06em] text-marino uppercase">
            Tienda de ejemplo
          </span>

          <h2 className="font-jakarta text-[clamp(30px,3.3cqi,46px)] leading-[1.08] font-extrabold tracking-[-0.03em] text-white text-balance">
            Cada tienda tiene su propia identidad
          </h2>

          <p className="max-w-[28em] text-[17px] leading-[1.55] text-[#D5DBE5] text-pretty">
            DealCommerce es claro y ordenado por dentro. Tu tienda, por fuera, se ve como tú quieras.
          </p>

          <Link
            href={TIENDA_DE_EJEMPLO}
            className="mt-2 inline-flex h-[52px] items-center gap-2 rounded-[12px] bg-white px-6 text-base font-semibold text-marino no-underline hover:bg-cielo hover:no-underline"
          >
            {NOMBRE_DE_EJEMPLO ? `Ver la tienda de ${NOMBRE_DE_EJEMPLO}` : "Ver una tienda de ejemplo"}{" "}
            <span aria-hidden="true">→</span>
          </Link>
        </div>

        <MaquetaDeVitrina />
      </div>
    </section>
  );
}

function MaquetaDeVitrina() {
  return (
    <div
      aria-hidden="true"
      className="overflow-hidden rounded-xl border border-[#2A2238] bg-[#0E0B14] shadow-[0_24px_60px_rgba(0,0,0,.35)]"
    >
      <div className="flex items-center justify-between border-b border-[#221B2E] px-[18px] py-3">
        <span className="font-serif text-xl text-white">{NOMBRE_DE_EJEMPLO ?? "Tu tienda"}</span>
        <span className="flex gap-3 text-[11px] text-[#C4B5FD]">
          <span>Inicio</span>
          <span>Catálogo</span>
          <span>Agendar visita</span>
        </span>
      </div>

      <div className="flex flex-col gap-4 p-[18px]">
        <div className="flex flex-col gap-2 rounded-lg bg-gradient-to-br from-[#3B2266] via-[#15101F] to-[#15101F] p-5">
          <span className="text-[10px] font-semibold tracking-[0.14em] text-[#C4B5FD] uppercase">Bienvenida</span>
          <span className="font-serif text-[28px] leading-[1.05] text-white">
            {NOMBRE_DE_EJEMPLO ?? "Tu tienda"}
          </span>
          <span className="text-xs text-[#D9D2EA]">Al por mayor y al detalle: por gramo, por lote y por pieza.</span>
          <div className="mt-1.5 flex gap-2">
            <span className="rounded-full bg-[#7C3AED] px-3 py-1.5 text-[11px] font-semibold text-white">
              Ver el catálogo
            </span>
            <span className="rounded-full border border-white/20 px-3 py-1.5 text-[11px] text-white">
              Agendar visita
            </span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2.5">
          {PRODUCTOS.map((producto) => (
            <div key={producto.nombre} className="flex flex-col gap-1 rounded-lg bg-[#17121F] p-2">
              <div className="aspect-square rounded-md bg-gradient-to-br from-[#D7D9E0] to-[#8D93A3] opacity-80" />
              <span className="mt-1 text-[10px] text-[#C4B5FD]">{producto.detalle}</span>
              <span className="truncate text-[11px] text-[#EDE9F6]">{producto.nombre}</span>
              <span className="text-xs font-bold text-white tabular-nums">{producto.precio}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
