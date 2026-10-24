import Link from "next/link";

import { formatearFechaLarga, sumarDias } from "@/lib/formato";
import type { RangoDeDias } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { IconoFlecha } from "./iconos";

/*
 * Navegación entre semanas de la agenda.
 *
 * Los límites los pone el backend en `ventana`: hasta dónde acepta visitas la
 * tienda. Acá no se decide nada, solo se dibuja lo que esa ventana permite.
 *
 * Son enlaces y no botones porque cada semana es una dirección propia: se puede
 * compartir, volver atrás y recargar sin perder dónde estaba.
 */
export function NavegacionSemana({
  base,
  rango,
  ventana,
  dias,
}: {
  base: string;
  rango: RangoDeDias;
  ventana: RangoDeDias;
  dias: number;
}) {
  const anterior = rango.desde > ventana.desde ? maximo(sumarDias(rango.desde, -dias), ventana.desde) : null;
  const siguiente = rango.hasta < ventana.hasta ? sumarDias(rango.hasta, 1) : null;

  return (
    <div className="flex items-center justify-between gap-4">
      <Paso href={anterior && `${base}?desde=${anterior}`} sentido="anterior">
        Semana anterior
      </Paso>

      <p className="text-center text-sm text-texto">
        {formatearFechaLarga(rango.desde)} al {formatearFechaLarga(rango.hasta)}
      </p>

      <Paso href={siguiente && `${base}?desde=${siguiente}`} sentido="siguiente">
        Semana siguiente
      </Paso>
    </div>
  );
}

function Paso({
  href,
  sentido,
  children,
}: {
  href: string | null;
  sentido: "anterior" | "siguiente";
  children: string;
}) {
  const clases = cn(
    "flex h-10 items-center gap-2 rounded-full border px-4 text-[13px] transition-colors",
    sentido === "siguiente" && "flex-row-reverse",
    href
      ? "cursor-pointer border-lila/30 text-texto hover:bg-violeta/14"
      : "border-lila/12 text-texto-suave/50",
  );

  const contenido = (
    <>
      <IconoFlecha tamano={13} sentido={sentido === "anterior" ? "izquierda" : "derecha"} />
      <span className="hidden sm:inline">{children}</span>
    </>
  );

  if (!href) {
    // Sin días hacia ese lado el paso se ve, pero no lleva a ninguna parte.
    return (
      <span aria-disabled="true" className={clases}>
        {contenido}
      </span>
    );
  }

  return (
    <Link href={href} aria-label={children} className={clases}>
      {contenido}
    </Link>
  );
}

function maximo(a: string, b: string): string {
  return a > b ? a : b;
}
