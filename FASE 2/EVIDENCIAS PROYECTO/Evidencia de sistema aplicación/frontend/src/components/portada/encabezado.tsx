"use client";

import Link from "next/link";
import { useState } from "react";

import { ENTRAR, SECCIONES, SOLICITAR_ACCESO } from "./enlaces";
import { Marca } from "./marca";

/*
 * Encabezado de la portada.
 *
 * El diseño trae dos variantes, escritorio y móvil, y el canvas las dibuja como
 * dos tarjetas de ancho fijo. Acá son la misma barra con un punto de quiebre:
 * bajo 1024 px se guarda la navegación y aparece el botón de menú, igual que en
 * la vitrina de la tienda.
 *
 * El desplegable no venía dibujado en el canvas. Se armó con los mismos
 * colores, bordes y tipografías del resto para que no se note de dónde salió.
 */
export function Encabezado() {
  const [abierto, setAbierto] = useState(false);

  return (
    <header
      onKeyDown={(evento) => evento.key === "Escape" && setAbierto(false)}
      className="sticky top-0 z-20 border-b border-arena bg-hueso/94 backdrop-blur-[8px]"
    >
      <div className="mx-auto flex max-w-[1280px] items-center justify-between gap-6 px-[clamp(20px,5.5cqi,80px)] py-[14px]">
        <Link href="/" className="flex items-center gap-2.5 text-marino no-underline hover:no-underline">
          <Marca />
        </Link>

        <nav aria-label="Principal" className="hidden items-center gap-8 text-[15px] font-medium lg:flex">
          {SECCIONES.map((seccion) => (
            <a key={seccion.href} href={seccion.href} className="text-marino no-underline hover:underline">
              {seccion.etiqueta}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-5 lg:flex">
          <Link href={ENTRAR} className="text-[15px] font-medium text-acero hover:text-acero-hondo">
            Iniciar sesión
          </Link>
          <Link
            href={SOLICITAR_ACCESO}
            className="inline-flex h-11 items-center rounded-[10px] bg-acero px-5 text-[15px] font-semibold text-white no-underline hover:bg-acero-hondo hover:no-underline"
          >
            Solicitar acceso
          </Link>
        </div>

        <button
          type="button"
          aria-label={abierto ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={abierto}
          aria-controls="menu-portada"
          onClick={() => setAbierto((estaba) => !estaba)}
          className="flex size-11 cursor-pointer items-center justify-center rounded-[10px] border border-arena-honda bg-white lg:hidden"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#14213D" strokeWidth="1.8" strokeLinecap="round">
            {abierto ? <path d="M5 5l10 10M15 5L5 15" /> : <path d="M3 6h14M3 10h14M3 14h14" />}
          </svg>
        </button>
      </div>

      {abierto && (
        <div
          id="menu-portada"
          className="border-t border-arena bg-hueso px-[clamp(20px,5.5cqi,80px)] pt-2 pb-5 lg:hidden"
        >
          <nav aria-label="Principal" className="flex flex-col">
            {SECCIONES.map((seccion) => (
              <a
                key={seccion.href}
                href={seccion.href}
                onClick={() => setAbierto(false)}
                className="border-b border-arena py-3.5 text-[15px] font-medium text-marino no-underline"
              >
                {seccion.etiqueta}
              </a>
            ))}
          </nav>

          <div className="mt-5 flex flex-col gap-3">
            <Link
              href={SOLICITAR_ACCESO}
              onClick={() => setAbierto(false)}
              className="flex h-12 items-center justify-center rounded-[12px] bg-acero text-[15px] font-semibold text-white no-underline hover:no-underline"
            >
              Solicitar acceso
            </Link>
            <Link
              href={ENTRAR}
              onClick={() => setAbierto(false)}
              className="flex h-12 items-center justify-center rounded-[12px] border border-niebla bg-white text-[15px] font-semibold text-acero no-underline hover:no-underline"
            >
              Iniciar sesión
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
