"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Isotipo } from "@/components/portada/marca";
import { useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";
import { cn } from "@/lib/utils";

/*
 * Barra superior de la administración de la plataforma.
 *
 * En marino, como la barra lateral del panel de una tienda: las dos son
 * herramientas de DealCommerce y se tienen que reconocer como de la misma
 * familia. Acá va arriba y no al costado porque son solo dos destinos.
 */

const DESTINOS = [
  { href: "/plataforma", texto: "Tiendas" },
  { href: "/plataforma/cuenta", texto: "Tu cuenta" },
];

export function BarraDePlataforma() {
  const { sesion } = useSesion();
  const ruta = usePathname();

  return (
    <header className="bg-marino text-[#C9D3DF]">
      <div className="mx-auto flex h-16 w-full max-w-[1280px] items-center gap-5 px-[clamp(20px,5.5cqi,80px)]">
        <Link href="/" className="flex items-center gap-2.5 text-white no-underline hover:no-underline">
          <span className="rounded-md bg-hueso p-0.5">
            <Isotipo tamano={22} />
          </span>
          <span className="hidden font-jakarta text-[16px] font-extrabold tracking-[-0.02em] sm:inline">
            DealCommerce
          </span>
        </Link>
        <span className="rounded-full bg-ambar px-2.5 py-0.5 text-[10.5px] font-bold text-marino uppercase">
          Administración
        </span>

        <nav aria-label="Administración" className="flex items-center gap-1">
          {DESTINOS.map((destino) => {
            const activo = ruta === destino.href;
            return (
              <Link
                key={destino.href}
                href={destino.href}
                aria-current={activo ? "page" : undefined}
                className={cn(
                  "rounded-lg px-3 py-1.5 text-[13.5px] no-underline hover:no-underline",
                  activo ? "bg-white font-semibold text-marino" : "text-[#DCE3EC] hover:bg-white/10 hover:text-white",
                )}
              >
                {destino.texto}
              </Link>
            );
          })}
        </nav>

        {sesion && (
          <div className="ml-auto flex items-center gap-3">
            <span className="hidden text-[13px] text-[#C9D3DF] md:inline">{sesion.usuario.nombre}</span>
            <button
              type="button"
              onClick={cerrarSesion}
              className="h-9 cursor-pointer rounded-lg border border-white/20 px-3.5 text-[13px] font-semibold text-white transition-colors hover:bg-white/10 motion-reduce:transition-none"
            >
              Salir
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
