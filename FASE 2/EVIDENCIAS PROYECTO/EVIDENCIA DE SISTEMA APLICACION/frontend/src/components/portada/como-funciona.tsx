"use client";

import { useState } from "react";

import { formatearPesos } from "@/lib/formato";
import { cn } from "@/lib/utils";

import { TituloDeSeccion } from "./secciones";

/*
 * Los tres pasos para tener la tienda andando.
 *
 * Va en una lista ordenada de verdad: el orden es parte del contenido, no de la
 * presentación. Cada paso trae una vista previa chica de lo que pasa en ese
 * momento: la planilla que se convierte en producto, el color de la marca que
 * se puede probar y el enlace que se puede copiar.
 */

const PASOS = [
  {
    titulo: "Sube tu catálogo desde Excel",
    detalle: "Usa la planilla que ya tienes. Ordenamos tus productos, fotos y tramos de precio.",
    vista: <Planilla />,
  },
  {
    titulo: "Dale tu estilo",
    detalle: "Elige colores, logo y tipografía. Tu tienda se ve como tu marca, no como la nuestra.",
    vista: <Estilos />,
  },
  {
    titulo: "Comparte el enlace y recibe pedidos",
    detalle:
      "Pégalo en tu bio de Instagram o mándalo por WhatsApp. Los pedidos llegan con el total calculado.",
    vista: <Enlace />,
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
              <div className="mt-auto pt-2">{paso.vista}</div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

const MARCO = "rounded-xl border border-arena bg-white p-4";

/** La planilla de siempre y el producto que sale de ella. */
function Planilla() {
  const filas = [
    ["CAD-50", "Cadena 925", 12990, 10990],
    ["ARO-12", "Aros argolla", 6490, 5490],
  ] as const;
  return (
    <div aria-hidden="true" className={cn(MARCO, "flex flex-col gap-3")}>
      <table className="w-full border-collapse text-[11.5px] tabular-nums">
        <thead>
          <tr className="bg-[#E7F2EA] text-left text-[#1E5E3B]">
            {["SKU", "Producto", "Precio", "+6 u."].map((c) => (
              <th key={c} className="border border-[#CFE3D5] px-1.5 py-1 font-semibold">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map(([sku, nombre, base, tramo]) => (
            <tr key={sku} className="text-marino">
              <td className="border border-arena px-1.5 py-1">{sku}</td>
              <td className="border border-arena px-1.5 py-1">{nombre}</td>
              <td className="border border-arena px-1.5 py-1">{base}</td>
              <td className="border border-arena px-1.5 py-1">{tramo}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center gap-2 text-xs text-pizarra">
        <span className="h-px flex-1 bg-arena" />
        se convierte en
        <span className="h-px flex-1 bg-arena" />
      </div>
      <div className="flex items-center gap-3 rounded-lg bg-hueso p-2.5">
        <span className="size-10 flex-none rounded-md bg-linear-to-br from-[#D9DEE6] to-[#B8C1CF]" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold text-marino">Cadena 925</p>
          <p className="text-xs text-pizarra tabular-nums">
            {formatearPesos(12990)} · desde 6 u. {formatearPesos(10990)}
          </p>
        </div>
      </div>
    </div>
  );
}

const PALETAS = [
  { nombre: "Noche", fondo: "#16121F", acento: "#8B5CF6", texto: "#F5F3FF" },
  { nombre: "Coral", fondo: "#FFF7F3", acento: "#E2583E", texto: "#3A1A12" },
  { nombre: "Bosque", fondo: "#F2F6F1", acento: "#2F6B4A", texto: "#14261B" },
];

/** Tres paletas para probar cómo cambia la tienda. */
function Estilos() {
  const [elegida, setElegida] = useState(0);
  const paleta = PALETAS[elegida];
  return (
    <div className={cn(MARCO, "flex flex-col gap-3")}>
      <div role="radiogroup" aria-label="Probar un estilo de tienda" className="flex gap-2">
        {PALETAS.map((p, i) => (
          <button
            key={p.nombre}
            type="button"
            role="radio"
            aria-checked={i === elegida}
            onClick={() => setElegida(i)}
            className={cn(
              "flex cursor-pointer items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
              i === elegida ? "border-marino bg-marino text-white" : "border-arena bg-hueso text-marino hover:border-niebla",
            )}
          >
            <span className="size-3 rounded-full ring-1 ring-black/10" style={{ background: p.acento }} />
            {p.nombre}
          </button>
        ))}
      </div>
      <div
        aria-hidden="true"
        className="flex flex-col gap-2.5 rounded-lg p-3.5 transition-colors duration-300 motion-reduce:transition-none"
        style={{ background: paleta.fondo, color: paleta.texto }}
      >
        <span className="font-jakarta text-sm font-extrabold tracking-[0.04em]">TU MARCA</span>
        <div className="grid grid-cols-2 gap-2">
          {[0, 1].map((n) => (
            <div key={n} className="flex flex-col gap-1">
              <span className="aspect-[4/3] rounded-md opacity-25" style={{ background: paleta.acento }} />
              <span className="h-1.5 w-3/4 rounded-full opacity-40" style={{ background: paleta.texto }} />
            </div>
          ))}
        </div>
        <span
          className="self-start rounded-full px-3 py-1 text-[11px] font-semibold text-white"
          style={{ background: paleta.acento }}
        >
          Ver catálogo
        </span>
      </div>
    </div>
  );
}

/** El enlace de la tienda, con un botón que lo copia de verdad. */
function Enlace() {
  const [copiado, setCopiado] = useState(false);
  const url = "dealcommerce.vercel.app/t/tu-tienda";

  async function copiar() {
    try {
      await navigator.clipboard.writeText(`https://${url}`);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 1800);
    } catch {
      setCopiado(false);
    }
  }

  return (
    <div className={cn(MARCO, "flex flex-col gap-3")}>
      <div className="flex items-center gap-2 rounded-lg border border-arena bg-hueso py-1.5 pr-1.5 pl-3">
        <span className="min-w-0 flex-1 truncate text-[13px] text-marino tabular-nums">{url}</span>
        <button
          type="button"
          onClick={copiar}
          className="h-8 flex-none cursor-pointer rounded-md bg-acero px-3 text-xs font-semibold text-white hover:bg-acero-hondo"
        >
          {copiado ? "¡Copiado!" : "Copiar"}
        </button>
      </div>
      <div aria-hidden="true" className="flex items-center gap-3 rounded-lg border border-ambar/40 bg-trigo/60 p-2.5">
        <span className="flex size-8 flex-none items-center justify-center rounded-full bg-ambar text-sm font-bold text-marino">
          1
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-[13px] font-semibold text-marino">Nuevo pedido · 8 productos</p>
          <p className="text-xs text-pizarra tabular-nums">Total calculado: {formatearPesos(186420)}</p>
        </div>
      </div>
    </div>
  );
}
