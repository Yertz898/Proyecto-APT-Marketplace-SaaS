"use client";

import Link from "next/link";

import { Marca } from "@/components/portada/marca";
import { useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";

/** Barra superior de la administración de la plataforma. */
export function BarraDePlataforma() {
  const { sesion } = useSesion();

  return (
    <header className="border-b border-arena bg-white">
      <div className="mx-auto flex h-16 w-full max-w-[1280px] items-center gap-6 px-[clamp(20px,5.5cqi,80px)]">
        <Link href="/" className="flex items-center gap-2.5 text-marino no-underline hover:no-underline">
          <Marca tamano={26} tamanoTexto={17} />
        </Link>
        <span className="rounded-full bg-cielo px-3 py-1 text-[11px] font-semibold text-acero">
          Administración
        </span>

        {sesion && (
          <div className="ml-auto flex items-center gap-4">
            <span className="hidden text-[13px] text-pizarra sm:inline">{sesion.usuario.nombre}</span>
            <button
              type="button"
              onClick={cerrarSesion}
              className="h-9 cursor-pointer rounded-[10px] border border-niebla px-4 text-[13px] font-semibold text-acero transition-colors hover:bg-cielo"
            >
              Salir
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
