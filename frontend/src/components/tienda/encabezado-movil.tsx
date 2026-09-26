"use client";

import Link from "next/link";
import { useState } from "react";

import { Sheet, SheetClose, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import type { IdentidadTienda } from "@/lib/tipos";

import { ContadorCarrito } from "./carrito";
import { IconoLupa } from "./iconos";
import { Marca } from "./marca";
import { clasesPanelLateral } from "./panel-lateral";

type Seccion = { href: string; etiqueta: string; activa: boolean };

/** Encabezado móvil con su panel lateral de menú. */
export function EncabezadoMovil({
  tienda,
  secciones,
}: {
  tienda: IdentidadTienda;
  secciones: Seccion[];
}) {
  const [abierto, setAbierto] = useState(false);

  return (
    <header className="border-b border-lila/14 bg-tinta/80 px-[18px] py-3.5 backdrop-blur-[16px] lg:hidden">
      <div className="flex items-center gap-3.5">
        <Sheet open={abierto} onOpenChange={setAbierto}>
          <SheetTrigger
            render={
              <button
                type="button"
                aria-label="Abrir menú"
                className="flex size-[34px] cursor-pointer flex-col justify-center gap-[5px] bg-transparent p-0"
              />
            }
          >
            <span className="block h-[1.6px] rounded-sm bg-texto" />
            <span className="block h-[1.6px] rounded-sm bg-texto" />
            <span className="block h-[1.6px] w-2/3 rounded-sm bg-lila" />
          </SheetTrigger>

          <SheetContent
            side="left"
            showCloseButton={false}
            overlayClassName={clasesPanelLateral.fondo}
            className={clasesPanelLateral.panel}
          >
            <div className="flex items-center justify-between">
              <SheetTitle className="font-serif text-[22px] font-normal text-texto">Menú</SheetTitle>
              <SheetClose
                render={
                  <button
                    type="button"
                    aria-label="Cerrar menú"
                    className="size-[34px] cursor-pointer rounded-full border border-lila/25 bg-transparent text-[15px] text-texto"
                  />
                }
              >
                ×
              </SheetClose>
            </div>

            <nav aria-label="Principal" className="mt-[26px] flex flex-col">
              {secciones.map((seccion) => (
                <Link
                  key={seccion.href}
                  href={seccion.href}
                  onClick={() => setAbierto(false)}
                  className="border-b border-texto/8 py-3.5 text-[15px] text-texto"
                >
                  {seccion.etiqueta}
                </Link>
              ))}
            </nav>

            <button
              type="button"
              aria-disabled="true"
              data-pendiente="iniciar-sesion"
              className="mt-[26px] h-[46px] w-full cursor-pointer rounded-[23px] border border-lila/40 bg-transparent text-[13px] font-medium text-texto"
            >
              Iniciar sesión
            </button>
          </SheetContent>
        </Sheet>

        <div className="mr-auto">
          <Marca tienda={tienda} lugar="movil" />
        </div>

        <button type="button" aria-label="Buscar" aria-disabled="true" data-pendiente="busqueda" className="block cursor-pointer">
          <IconoLupa tamano={19} claro />
        </button>

        <ContadorCarrito variante="movil" />
      </div>
    </header>
  );
}
