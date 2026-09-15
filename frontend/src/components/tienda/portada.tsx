import Link from "next/link";
import { Fragment } from "react";

import type { ContenidoTienda } from "@/lib/tipos";

/** Portada de la tienda (mockup 1A en escritorio, 1D en móvil). */
export function Portada({ tienda }: { tienda: ContenidoTienda }) {
  const { portada } = tienda;
  const catalogo = `/t/${tienda.slug}/catalogo`;

  return (
    <>
      <section className="hidden overflow-hidden bg-[radial-gradient(80%_120%_at_78%_10%,rgba(124,58,237,.32)_0%,rgba(11,10,15,0)_62%),linear-gradient(180deg,#0F0D16_0%,#0B0A0F_100%)] lg:block">
        <div className="relative mx-auto max-w-[1440px] px-20 pt-[82px] pb-[76px]">
          <div
            aria-hidden="true"
            className="absolute top-14 right-24 flex size-[330px] items-center justify-center rounded-full border border-lila/22 bg-[radial-gradient(60%_60%_at_40%_30%,rgba(167,139,250,.18),rgba(11,10,15,0)_70%)]"
          >
            <svg width="210" height="210" viewBox="0 0 100 100" fill="none">
              <circle cx="50" cy="60" r="26" stroke="#A78BFA" strokeWidth="2.2" />
              <path d="M50 14l14 14-14 14-14-14 14-14z" fill="#C9A227" />
              <path d="M50 14l14 14H36l14-14z" fill="#F5F3F7" opacity=".32" />
            </svg>
          </div>

          <div className="relative max-w-[600px]">
            <p className="text-[11px] font-semibold tracking-[.18em] text-lila uppercase">{portada.antetitulo}</p>
            <h1 className="mt-[18px] font-serif text-[62px] leading-[1.04] font-medium text-pretty text-texto">
              {portada.titulo}
            </h1>
            <p className="mt-5 max-w-[470px] text-base leading-[1.65] text-texto-suave">{portada.descripcion}</p>

            <div className="mt-[34px] flex gap-3.5">
              <Link
                href={catalogo}
                className="inline-flex h-[50px] items-center rounded-full bg-violeta px-[26px] text-sm font-semibold text-white transition-colors hover:bg-violeta-hover"
              >
                Ver catálogo
              </Link>
              <button
                type="button"
                aria-disabled="true"
                data-pendiente="precios-mayoristas"
                className="h-[50px] cursor-pointer rounded-full border border-lila/38 bg-transparent px-[26px] text-sm font-medium text-texto transition-colors hover:bg-violeta/16"
              >
                Precios mayoristas
              </button>
            </div>

            <ul className="mt-9 flex gap-[30px] text-xs text-texto-suave">
              {portada.garantias.map((garantia, indice) => (
                <Fragment key={garantia}>
                  {indice > 0 && <li aria-hidden="true">·</li>}
                  <li>{garantia}</li>
                </Fragment>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="bg-[radial-gradient(90%_100%_at_80%_0%,rgba(124,58,237,.34)_0%,rgba(11,10,15,0)_62%),linear-gradient(180deg,#100E18,#0B0A0F)] px-5 pt-[34px] pb-9 lg:hidden">
        <p className="text-[10px] font-semibold tracking-[.18em] text-lila uppercase">{portada.movil.antetitulo}</p>
        <h1 className="mt-3 font-serif text-[38px] leading-[1.08] font-medium text-pretty text-texto">
          {portada.movil.titulo}
        </h1>
        <p className="mt-3 text-sm leading-[1.6] text-texto-suave">{portada.movil.descripcion}</p>

        <Link
          href={catalogo}
          className="mt-[22px] flex h-[50px] w-full items-center justify-center rounded-full bg-violeta text-sm font-semibold text-white"
        >
          Ver catálogo
        </Link>

        <div aria-hidden="true" className="mt-[26px] flex justify-center">
          <div className="flex size-[180px] items-center justify-center rounded-full border border-lila/22 bg-[radial-gradient(60%_60%_at_40%_30%,rgba(167,139,250,.18),rgba(11,10,15,0)_72%)]">
            <svg width="120" height="120" viewBox="0 0 100 100" fill="none">
              <circle cx="50" cy="60" r="26" stroke="#A78BFA" strokeWidth="2.4" />
              <path d="M50 14l14 14-14 14-14-14 14-14z" fill="#C9A227" />
            </svg>
          </div>
        </div>
      </section>
    </>
  );
}
