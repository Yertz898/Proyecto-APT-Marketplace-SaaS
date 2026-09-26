"use client";

import Image from "next/image";

import { formatearPesos } from "@/lib/formato";
import type { Lote } from "@/lib/tipos";

import { useCarrito } from "./carrito";
import { InsigniaCupos } from "./cupos";

/*
 * Ficha de lote.
 *
 * El lote se agrega completo: no hay selectores de material ni talla. Lo que se
 * compra es una composición, no piezas concretas, y por eso la advertencia de
 * que los modelos varían va visible y no en letra chica.
 */
export function FichaLote({ lote }: { lote: Lote }) {
  const { agregar } = useCarrito();

  return (
    <div className="mx-auto grid max-w-[1280px] items-start gap-10 px-5 pt-[26px] pb-[70px] lg:grid-cols-[minmax(0,1fr)_460px] lg:px-6">
      <div>
        {lote.foto && (
          <div className="relative h-[360px] overflow-hidden rounded-[20px] border border-lila/14 lg:h-[520px]">
            <Image
              src={lote.foto.url}
              alt={lote.foto.alt}
              fill
              sizes="(min-width: 1024px) 700px, 100vw"
              className="object-cover"
            />
          </div>
        )}

        <section className="mt-8">
          <h2 className="font-serif text-[26px] font-medium text-texto">Qué trae este lote</h2>
          <ul className="mt-4 flex flex-col gap-2">
            {lote.composicion.map((parte) => (
              <li
                key={parte.categoria}
                className="flex items-center justify-between rounded-xl border border-lila/12 bg-superficie px-4 py-3 text-sm"
              >
                <span className="text-texto-suave">{parte.categoria}</span>
                <span className="text-texto">{parte.cantidad} piezas</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div>
        <div className="flex items-start justify-between gap-4">
          <h1 className="font-serif text-[36px] leading-[1.1] font-medium text-texto lg:text-[42px]">
            {lote.nombre}
          </h1>
          <InsigniaCupos cupos={lote.cupos} agotado={lote.agotado} />
        </div>

        <p className="mt-3 text-[13px] text-texto-suave">
          {lote.piezasTotales} piezas · {lote.material}
        </p>

        <p className="mt-6 font-serif text-[40px] font-semibold text-oro">{formatearPesos(lote.precioNeto)}</p>
        <p className="text-[13px] text-texto-suave">
          neto · {formatearPesos(lote.precioTotal)} con IVA incluido
        </p>

        <p className="mt-6 rounded-xl border border-oro/28 bg-oro/8 p-4 text-sm leading-[1.6] text-texto">
          Los modelos pueden variar según disponibilidad.
        </p>

        {lote.agotado ? (
          <p className="mt-6 rounded-full border border-lila/20 py-4 text-center text-sm text-texto-suave">
            Este lote ya no tiene cupos disponibles
          </p>
        ) : (
          <button
            type="button"
            onClick={() => agregar(1)}
            className="mt-6 h-[54px] w-full cursor-pointer rounded-full bg-violeta text-[15px] font-semibold text-white transition-colors hover:bg-violeta-hover"
          >
            Agregar al carrito
          </button>
        )}
      </div>
    </div>
  );
}
