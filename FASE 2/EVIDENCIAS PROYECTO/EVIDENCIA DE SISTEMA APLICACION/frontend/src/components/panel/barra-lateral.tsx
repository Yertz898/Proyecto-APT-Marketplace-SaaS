"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { Isotipo } from "@/components/portada/marca";
import { useSesion } from "@/components/sesion/usar-sesion";
import { cerrarSesion } from "@/lib/api/sesion";
import { cn } from "@/lib/utils";

import {
  NOMBRE_DEL_PLAN,
  planAlcanza,
  porGrupo,
  rolAlcanza,
  seccionDe,
  type Seccion,
} from "./secciones";

/*
 * Barra lateral del panel.
 *
 * Son catorce secciones: en una barra horizontal no caben, y apiñadas no se
 * encuentran. Agrupadas en una lateral se recorren de un vistazo.
 *
 * Va en marino, el color de la marca, para que la herramienta se distinga del
 * trabajo: la barra es oscura y la columna de contenido, clara. Arriba va la
 * tienda con su plan y el enlace a la vitrina, que es lo que el dueño más
 * busca; abajo, quién está conectado.
 *
 * Cada ítem dice en qué está sin que haya que entrar: candado si el plan no lo
 * incluye, un punto si los datos son de ejemplo, y "pronto" lo que todavía no
 * existe. Es información, no protección: quien decide es el backend.
 *
 * En pantallas chicas la barra es un cajón que entra desde la izquierda.
 */
export function BarraLateral() {
  const [abierta, setAbierta] = useState(false);
  const ruta = usePathname();
  const [rutaVista, setRutaVista] = useState(ruta);

  // Al navegar se cierra el cajón: si no, la página nueva queda tapada.
  if (rutaVista !== ruta) {
    setRutaVista(ruta);
    setAbierta(false);
  }

  // Con el cajón abierto, Escape lo cierra y el fondo no se desplaza.
  useEffect(() => {
    if (!abierta) return;
    const cerrar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") setAbierta(false);
    };
    document.addEventListener("keydown", cerrar);
    const desborde = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", cerrar);
      document.body.style.overflow = desborde;
    };
  }, [abierta]);

  return (
    <>
      <BarraMovil onAbrir={() => setAbierta(true)} />

      {abierta && (
        <button
          type="button"
          aria-label="Cerrar menú"
          onClick={() => setAbierta(false)}
          className="fixed inset-0 z-40 cursor-default bg-marino/40 backdrop-blur-[2px] lg:hidden"
        />
      )}

      <aside
        id="menu-del-panel"
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-[272px] max-w-[85vw] bg-marino text-[#C9D3DF] transition-transform duration-200 ease-out motion-reduce:transition-none",
          "lg:sticky lg:top-0 lg:z-auto lg:h-dvh lg:w-[256px] lg:max-w-none lg:shrink-0 lg:translate-x-0",
          abierta ? "translate-x-0 shadow-2xl" : "-translate-x-full",
        )}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between gap-2 px-5 pt-5 pb-4">
            <Link href="/" className="flex items-center gap-2.5 text-white no-underline hover:no-underline">
              <span className="rounded-md bg-hueso p-0.5">
                <Isotipo tamano={22} />
              </span>
              <span className="font-jakarta text-[16px] font-extrabold tracking-[-0.02em]">DealCommerce</span>
            </Link>
            <button
              type="button"
              aria-label="Cerrar menú"
              onClick={() => setAbierta(false)}
              className="flex size-9 cursor-pointer items-center justify-center rounded-lg text-white/80 hover:bg-white/10 lg:hidden"
            >
              <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" aria-hidden="true">
                <path d="M5 5l10 10M15 5L5 15" />
              </svg>
            </button>
          </div>

          <TarjetaDeTienda />
          <Menu />
          <PieDeLaBarra />
        </div>
      </aside>
    </>
  );
}

function BarraMovil({ onAbrir }: { onAbrir: () => void }) {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-arena bg-white/95 px-5 py-3 backdrop-blur lg:hidden">
      <Link href="/panel" className="flex items-center gap-2.5 text-marino no-underline hover:no-underline">
        <Isotipo tamano={24} />
        <span className="font-jakarta text-[16px] font-extrabold tracking-[-0.02em]">DealCommerce</span>
      </Link>

      <button
        type="button"
        aria-label="Abrir menú"
        aria-controls="menu-del-panel"
        onClick={onAbrir}
        className="flex size-10 cursor-pointer items-center justify-center rounded-[10px] border border-arena-honda"
      >
        <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="#14213D" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true">
          <path d="M3 6h14M3 10h14M3 14h14" />
        </svg>
      </button>
    </header>
  );
}

function TarjetaDeTienda() {
  const { sesion } = useSesion();
  const tienda = sesion?.usuario.tienda;
  if (!tienda) return null;

  return (
    <div className="mx-3 mb-2 rounded-xl bg-white/[0.06] p-3.5 ring-1 ring-white/10">
      <div className="flex items-start justify-between gap-2">
        <p className="min-w-0 truncate font-jakarta text-[15px] font-bold text-white">{tienda.nombre}</p>
        <span className="flex-none rounded-full bg-ambar px-2 py-0.5 text-[10px] font-bold text-marino uppercase">
          {NOMBRE_DEL_PLAN[tienda.plan]}
        </span>
      </div>
      <a
        href={`/t/${tienda.slug}`}
        target="_blank"
        rel="noreferrer"
        className="mt-2 inline-flex items-center gap-1.5 text-[12.5px] text-[#C9D3DF] no-underline hover:text-white hover:underline"
      >
        Ver mi tienda
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true">
          <path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1h5" />
        </svg>
        <span className="sr-only">(se abre en otra pestaña)</span>
      </a>
    </div>
  );
}

function Menu() {
  const ruta = usePathname();
  const { sesion } = useSesion();
  const rol = sesion?.usuario.rol;
  const plan = sesion?.usuario.tienda?.plan;

  // Una sola sección activa, la más específica. Comparar ruta por ruta dejaría
  // «Inicio» encendido en todas, porque /panel es prefijo de todo el panel.
  const actual = seccionDe(ruta);

  return (
    <nav aria-label="Secciones del panel" className="flex-1 overflow-y-auto px-3 py-3">
      {porGrupo().map(([grupo, secciones]) => {
        const visibles = secciones.filter((s) => rolAlcanza(rol, s));
        if (visibles.length === 0) return null;

        return (
          <div key={grupo} className="mb-4 last:mb-0">
            {grupo && (
              <p className="px-2.5 pb-1.5 text-[10.5px] font-semibold tracking-[0.08em] text-[#8B9AB0] uppercase">
                {grupo}
              </p>
            )}

            <ul className="flex list-none flex-col gap-0.5 p-0">
              {visibles.map((seccion) => (
                <li key={seccion.href}>
                  <Enlace
                    seccion={seccion}
                    activa={actual?.href === seccion.href}
                    bloqueada={!planAlcanza(plan, seccion.plan)}
                  />
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </nav>
  );
}

function Enlace({ seccion, activa, bloqueada }: { seccion: Seccion; activa: boolean; bloqueada: boolean }) {
  const clases = cn(
    "flex items-center gap-2.5 rounded-lg px-2.5 py-[7px] text-[14px] no-underline transition-colors hover:no-underline motion-reduce:transition-none",
    activa ? "bg-white font-semibold text-marino" : "text-[#DCE3EC] hover:bg-white/[0.08] hover:text-white",
    bloqueada && "text-[#8B9AB0] hover:bg-transparent hover:text-[#8B9AB0]",
  );

  const contenido = (
    <>
      <span className={activa ? "text-acero" : "text-[#8B9AB0]"}>{seccion.icono}</span>
      <span className="flex-1 truncate">{seccion.etiqueta}</span>
      <Distintivo seccion={seccion} bloqueada={bloqueada} />
    </>
  );

  if (bloqueada || seccion.estado === "proximamente") {
    // No lleva a ninguna parte, pero se ve: así el dueño sabe qué existe y qué
    // le falta para tenerlo.
    return (
      <span aria-disabled="true" className={cn(clases, "cursor-default")}>
        {contenido}
      </span>
    );
  }

  return (
    <Link href={seccion.href} aria-current={activa ? "page" : undefined} className={clases}>
      {contenido}
    </Link>
  );
}

/** El distintivo de la derecha: candado, punto de demostración o "pronto". */
function Distintivo({ seccion, bloqueada }: { seccion: Seccion; bloqueada: boolean }) {
  if (bloqueada) {
    return (
      <span title={`Disponible en el plan ${NOMBRE_DEL_PLAN[seccion.plan]}`}>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-label="Bloqueado por tu plan">
          <rect x="5" y="11" width="14" height="9" rx="2" />
          <path d="M8 11V8a4 4 0 018 0v3" />
        </svg>
      </span>
    );
  }

  if (seccion.estado === "proximamente") {
    return <span className="text-[10px] font-semibold">pronto</span>;
  }

  if (seccion.estado === "demostracion") {
    return <span title="Datos de ejemplo" className="size-[6px] rounded-full bg-ambar" />;
  }

  return null;
}

function PieDeLaBarra() {
  const { sesion } = useSesion();
  if (!sesion) return null;

  const inicial = sesion.usuario.nombre.trim().charAt(0).toUpperCase() || "?";

  return (
    <div className="border-t border-white/10 px-4 py-3.5">
      <div className="flex items-center gap-2.5">
        <span className="flex size-8 flex-none items-center justify-center rounded-full bg-acero text-[13px] font-bold text-white">
          {inicial}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold text-white">{sesion.usuario.nombre}</p>
          <p className="truncate text-[11.5px] text-[#8B9AB0]">{sesion.usuario.rolNombre}</p>
        </div>
        <button
          type="button"
          onClick={cerrarSesion}
          title="Cerrar sesión"
          aria-label="Cerrar sesión"
          className="flex size-8 flex-none cursor-pointer items-center justify-center rounded-lg text-[#C9D3DF] hover:bg-white/10 hover:text-white"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M15 4h3a2 2 0 012 2v12a2 2 0 01-2 2h-3M10 17l-5-5 5-5M5 12h11" />
          </svg>
        </button>
      </div>
    </div>
  );
}
