"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";
import { cn } from "@/lib/utils";

const SECCIONES = [{ href: "/panel/cargas", etiqueta: "Carga masiva" }];

/** Barra superior del panel. */
export function NavegacionPanel() {
  const ruta = usePathname();
  const { sesion } = useSesion();

  return (
    <header className="border-b border-lila/14 bg-superficie">
      <div className="mx-auto flex h-16 w-full max-w-[1100px] items-center gap-8 px-5 lg:px-8">
        <span className="font-serif text-xl text-texto">
          {/* La tienda del panel sale de la sesión, nunca de la dirección. */}
          {sesion?.usuario.tienda?.nombre ?? "Panel"}
        </span>

        <nav aria-label="Secciones del panel" className="flex items-center gap-6 text-sm text-texto-suave">
          {SECCIONES.map((seccion) => (
            <Link
              key={seccion.href}
              href={seccion.href}
              className={cn(
                "transition-colors hover:text-texto",
                ruta.startsWith(seccion.href) && "text-texto",
              )}
            >
              {seccion.etiqueta}
            </Link>
          ))}
        </nav>

        {sesion && (
          <div className="ml-auto flex items-center gap-4">
            <span className="hidden text-[13px] text-texto-suave sm:inline">
              {sesion.usuario.nombre} · {sesion.usuario.rolNombre}
            </span>
            <button
              type="button"
              onClick={cerrarSesion}
              className="h-9 cursor-pointer rounded-full border border-lila/30 px-4 text-[13px] text-texto transition-colors hover:bg-violeta/18"
            >
              Salir
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
