"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const SECCIONES = [{ href: "/panel/cargas", etiqueta: "Carga masiva" }];

/** Barra superior del panel. */
export function NavegacionPanel() {
  const ruta = usePathname();

  return (
    <header className="border-b border-lila/14 bg-superficie">
      <div className="mx-auto flex h-16 w-full max-w-[1100px] items-center gap-8 px-5 lg:px-8">
        <span className="font-serif text-xl text-texto">Panel</span>

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

        <span
          data-pendiente="sesion"
          className="ml-auto rounded-full border border-oro/40 bg-oro/8 px-3 py-1 text-[11px] text-oro"
        >
          Sin sesión: pendiente de autenticación
        </span>
      </div>
    </header>
  );
}
