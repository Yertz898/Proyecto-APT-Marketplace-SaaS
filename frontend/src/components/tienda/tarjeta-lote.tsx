import Image from "next/image";
import Link from "next/link";

import { formatearPesos } from "@/lib/formato";
import type { Lote } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { InsigniaCupos } from "./cupos";

/*
 * Tarjeta de lote.
 *
 * Un lote se compra entero: no hay selectores. Si todavía no tiene foto cargada,
 * el espacio de la imagen no se dibuja.
 *
 * Un lote agotado no se ofrece como comprable.
 */
export function TarjetaLote({ slugTienda, lote }: { slugTienda: string; lote: Lote }) {
  const ficha = `/t/${slugTienda}/lotes/${lote.codigo}`;

  return (
    <article
      className={cn(
        "flex flex-col overflow-hidden rounded-[14px] border border-lila/10 bg-superficie transition-[border-color] duration-250 lg:rounded-2xl",
        lote.agotado ? "opacity-60" : "hover:border-lila/55",
      )}
    >
      {lote.foto && (
        <div className="relative h-48 lg:h-[250px]">
          <Image
            src={lote.foto.url}
            alt={lote.foto.alt}
            fill
            sizes="(min-width: 1024px) 25vw, 50vw"
            className="object-cover"
          />
        </div>
      )}

      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-start justify-between gap-3">
          <h3 className="font-serif text-[19px] leading-[1.2] text-texto lg:text-[21px]">{lote.nombre}</h3>
          <InsigniaCupos cupos={lote.cupos} agotado={lote.agotado} />
        </div>

        <p className="mt-1 text-xs text-texto-suave">
          {lote.piezasTotales} piezas · {lote.material}
        </p>

        <ul className="mt-3 flex flex-wrap gap-1.5">
          {lote.composicion.map((parte) => (
            <li key={parte.categoria} className="rounded-md border border-lila/16 px-2 py-1 text-[11px] text-texto-suave">
              {parte.cantidad} {parte.categoria}
            </li>
          ))}
        </ul>

        <p className="mt-4">
          <span className="font-serif text-[23px] font-semibold text-oro">{formatearPesos(lote.precioNeto)}</span>
          <span className="ml-2 text-[11px] text-texto-suave">neto</span>
        </p>
        <p className="text-xs text-texto-suave">{formatearPesos(lote.precioTotal)} con IVA</p>

        <p className="mt-3 text-xs text-texto-suave">Los modelos pueden variar según disponibilidad</p>

        {lote.agotado ? (
          <p className="mt-4 rounded-[11px] border border-lila/20 py-2.5 text-center text-[13px] text-texto-suave">
            Sin cupos disponibles
          </p>
        ) : (
          <Link
            href={ficha}
            className="mt-4 flex h-10 items-center justify-center rounded-[11px] bg-violeta text-[13px] font-semibold text-white transition-colors hover:bg-violeta-hover"
          >
            Ver lote
          </Link>
        )}
      </div>
    </article>
  );
}
