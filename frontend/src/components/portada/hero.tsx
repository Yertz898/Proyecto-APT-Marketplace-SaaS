import Link from "next/link";

import { SOLICITAR_ACCESO } from "./enlaces";
import { MaquetaTienda } from "./maqueta-tienda";

/*
 * Titular de la portada.
 *
 * Las dos columnas se arman con auto-fit y un mínimo de 480 px: sobre ese ancho
 * van lado a lado y bajo él se apilan solas, sin punto de quiebre escrito.
 */
export function Hero() {
  return (
    <section className="px-[clamp(20px,5.5cqi,80px)] pt-[clamp(48px,6cqi,96px)] pb-[clamp(64px,7cqi,112px)]">
      <div className="mx-auto grid max-w-[1280px] grid-cols-[repeat(auto-fit,minmax(min(100%,480px),1fr))] items-center gap-[clamp(48px,5cqi,72px)]">
        <div className="flex flex-col items-start gap-6">
          <span className="inline-flex items-center gap-2 text-[13px] font-semibold tracking-[0.06em] text-acero uppercase">
            <span className="size-2 rounded-[2px] bg-ambar" />
            Para tiendas mayoristas en Chile
          </span>

          <h1 className="font-jakarta text-[clamp(42px,5cqi,72px)] leading-[1.02] font-extrabold tracking-[-0.035em] text-balance">
            Deja de cotizar por WhatsApp.
          </h1>

          <p className="max-w-[30em] text-[clamp(18px,1.45cqi,21px)] leading-[1.5] text-pizarra text-pretty">
            Tu catálogo mayorista en línea, con precios por volumen que se calculan solos.
          </p>

          <div className="mt-2 flex w-full flex-wrap gap-3">
            <Link
              href={SOLICITAR_ACCESO}
              className="inline-flex h-[52px] shrink items-center justify-center rounded-[12px] bg-acero px-[26px] text-base font-semibold text-white no-underline hover:bg-acero-hondo hover:no-underline"
            >
              Solicitar acceso
            </Link>
            <a
              href="#ejemplo"
              className="inline-flex h-[52px] shrink items-center justify-center gap-2 rounded-[12px] border border-niebla bg-white px-6 text-base font-semibold text-acero no-underline hover:border-acero hover:no-underline"
            >
              Ver una tienda de ejemplo <span aria-hidden="true">→</span>
            </a>
          </div>

          <p className="mt-1 text-sm text-pizarra">
            Sin instalar nada. Si usas WhatsApp, puedes usar DealCommerce.
          </p>
        </div>

        <MaquetaTienda />
      </div>
    </section>
  );
}
