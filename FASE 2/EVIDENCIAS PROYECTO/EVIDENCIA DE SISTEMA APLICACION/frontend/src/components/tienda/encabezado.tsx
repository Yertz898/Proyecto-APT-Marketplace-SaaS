"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import type { IdentidadTienda } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { ContadorCarrito } from "./carrito";
import { Cuenta } from "./cuenta";
import { EncabezadoMovil } from "./encabezado-movil";
import { IconoLupa } from "./iconos";
import { Marca } from "./marca";

/*
 * Encabezado de la tienda pública.
 *
 * El menú es el mismo para toda tienda: inicio, catálogo y agenda. Cómo vende
 * cada una —por unidad, por lote o por peso— se agrupa dentro del catálogo, con
 * los datos del backend. Las categorías tampoco van acá: cambian entre tiendas.
 *
 * Los elementos con `data-pendiente` llevan a pantallas que todavía no existen.
 */
export function Encabezado({ tienda }: { tienda: IdentidadTienda }) {
  const ruta = usePathname();
  const base = `/t/${tienda.slug}`;

  const secciones = [
    { href: base, etiqueta: "Inicio", activa: ruta === base },
    {
      href: `${base}/productos`,
      etiqueta: "Catálogo",
      activa: ruta.startsWith(`${base}/productos`),
    },
    {
      href: `${base}/agenda`,
      etiqueta: "Agendar visita",
      activa: ruta.startsWith(`${base}/agenda`),
    },
  ];

  return (
    <>
      <header className="relative z-40 hidden border-b border-lila/14 bg-tinta/74 backdrop-blur-[16px] lg:block">
        <div className="mx-auto flex h-[78px] max-w-[1280px] items-center gap-10 px-6">
          <Marca tienda={tienda} lugar="encabezado" />

          <nav aria-label="Principal" className="flex items-center gap-[30px] text-sm text-texto-suave">
            {secciones.map((seccion) => (
              <Link
                key={seccion.href}
                href={seccion.href}
                className={cn("transition-colors hover:text-texto", seccion.activa && "text-texto")}
              >
                {seccion.etiqueta}
              </Link>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-4">
            <div
              data-pendiente="busqueda"
              className="flex h-10 w-[230px] items-center gap-[9px] rounded-[20px] border border-lila/16 bg-texto/5 px-3.5"
            >
              <IconoLupa tamano={15} />
              <span className="text-[13px] text-texto-suave">Buscar</span>
            </div>

            <ContadorCarrito variante="escritorio" />

            <Cuenta slug={tienda.slug} variante="escritorio" />
          </div>
        </div>
      </header>

      <EncabezadoMovil tienda={tienda} secciones={secciones} />
    </>
  );
}
