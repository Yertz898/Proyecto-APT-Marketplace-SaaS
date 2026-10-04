"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Marca } from "@/components/portada/marca";
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
 * Son quince secciones: en una barra horizontal no caben, y apiñadas no se
 * encuentran. Agrupadas en una lateral se recorren de un vistazo.
 *
 * Cada ítem dice en qué está sin que haya que entrar: candado si el plan no lo
 * incluye, un punto si los datos son de ejemplo, y "pronto" lo que todavía no
 * existe. Es información, no protección: quien decide es el backend.
 */
export function BarraLateral() {
  const [abierta, setAbierta] = useState(false);

  return (
    <>
      <BarraMovil abierta={abierta} onAlternar={() => setAbierta((v) => !v)} />

      <aside
        className={cn(
          "border-arena bg-white lg:sticky lg:top-0 lg:block lg:h-dvh lg:w-[248px] lg:shrink-0 lg:border-r",
          abierta ? "block border-b" : "hidden",
        )}
      >
        <div className="flex h-full flex-col">
          <div className="hidden items-center gap-2.5 border-b border-arena px-5 py-[18px] lg:flex">
            <Link href="/" className="flex items-center gap-2.5 text-marino no-underline hover:no-underline">
              <Marca tamano={24} tamanoTexto={16} />
            </Link>
          </div>

          <Menu onNavegar={() => setAbierta(false)} />
          <PieDeLaBarra />
        </div>
      </aside>
    </>
  );
}

function BarraMovil({ abierta, onAlternar }: { abierta: boolean; onAlternar: () => void }) {
  return (
    <header className="flex items-center justify-between border-b border-arena bg-white px-5 py-3 lg:hidden">
      <Link href="/panel" className="flex items-center gap-2.5 text-marino no-underline hover:no-underline">
        <Marca tamano={24} tamanoTexto={16} />
      </Link>

      <button
        type="button"
        aria-label={abierta ? "Cerrar menú" : "Abrir menú"}
        aria-expanded={abierta}
        onClick={onAlternar}
        className="flex size-10 cursor-pointer items-center justify-center rounded-[10px] border border-arena-honda"
      >
        <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="#14213D" strokeWidth="1.8" strokeLinecap="round">
          {abierta ? <path d="M5 5l10 10M15 5L5 15" /> : <path d="M3 6h14M3 10h14M3 14h14" />}
        </svg>
      </button>
    </header>
  );
}

function Menu({ onNavegar }: { onNavegar: () => void }) {
  const ruta = usePathname();
  const { sesion } = useSesion();
  const rol = sesion?.usuario.rol;
  const plan = sesion?.usuario.tienda?.plan;

  // Una sola sección activa, la más específica. Comparar ruta por ruta dejaría
  // «Inicio» encendido en todas, porque /panel es prefijo de todo el panel.
  const actual = seccionDe(ruta);

  return (
    <nav aria-label="Secciones del panel" className="flex-1 overflow-y-auto px-3 py-4">
      {porGrupo().map(([grupo, secciones]) => {
        const visibles = secciones.filter((s) => rolAlcanza(rol, s));
        if (visibles.length === 0) return null;

        return (
          <div key={grupo} className="mb-5 last:mb-0">
            {grupo && (
              <p className="px-2 pb-1.5 text-[11px] font-semibold tracking-[0.06em] text-pizarra uppercase">
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
                    onNavegar={onNavegar}
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

function Enlace({
  seccion,
  activa,
  bloqueada,
  onNavegar,
}: {
  seccion: Seccion;
  activa: boolean;
  bloqueada: boolean;
  onNavegar: () => void;
}) {
  const clases = cn(
    "flex items-center gap-2.5 rounded-[10px] px-2.5 py-2 text-[14px] no-underline transition-colors hover:no-underline",
    activa ? "bg-cielo font-semibold text-acero" : "text-marino hover:bg-hueso",
    bloqueada && "text-pizarra",
  );

  const contenido = (
    <>
      <span className={activa ? "text-acero" : "text-pizarra"}>{seccion.icono}</span>
      <span className="flex-1 truncate">{seccion.etiqueta}</span>
      <Marca_ seccion={seccion} bloqueada={bloqueada} />
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
    <Link href={seccion.href} onClick={onNavegar} aria-current={activa ? "page" : undefined} className={clases}>
      {contenido}
    </Link>
  );
}

/** El distintivo de la derecha: candado, punto de demostración o "pronto". */
function Marca_({ seccion, bloqueada }: { seccion: Seccion; bloqueada: boolean }) {
  if (bloqueada) {
    return (
      <span title={`Disponible en el plan ${NOMBRE_DEL_PLAN[seccion.plan]}`} className="text-pizarra">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-label="Bloqueado por tu plan">
          <rect x="5" y="11" width="14" height="9" rx="2" />
          <path d="M8 11V8a4 4 0 018 0v3" />
        </svg>
      </span>
    );
  }

  if (seccion.estado === "proximamente") {
    return <span className="text-[10px] font-semibold text-pizarra">pronto</span>;
  }

  if (seccion.estado === "demostracion") {
    return <span title="Datos de ejemplo" className="size-[6px] rounded-full bg-ambar" />;
  }

  return null;
}

function PieDeLaBarra() {
  const { sesion } = useSesion();
  if (!sesion) return null;

  const tienda = sesion.usuario.tienda;

  return (
    <div className="border-t border-arena px-4 py-3.5">
      {tienda && (
        <p className="truncate text-[13px] font-semibold text-marino">{tienda.nombre}</p>
      )}
      <p className="truncate text-[12px] text-pizarra">
        {sesion.usuario.nombre} · {sesion.usuario.rolNombre}
      </p>
      {tienda && (
        <p className="mt-1 text-[11px] text-pizarra">Plan {NOMBRE_DEL_PLAN[tienda.plan]}</p>
      )}

      <button
        type="button"
        onClick={cerrarSesion}
        className="mt-3 h-9 w-full cursor-pointer rounded-[10px] border border-niebla text-[13px] font-semibold text-acero transition-colors hover:bg-cielo"
      >
        Cerrar sesión
      </button>
    </div>
  );
}
