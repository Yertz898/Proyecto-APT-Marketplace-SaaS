"use client";

import { useState } from "react";

import { diaDe, formatearDiaLargo, formatearHora } from "@/lib/formato";
import type { HoraDisponible } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { ReservaDeVisita } from "./reserva-visita";

/*
 * Selección de la hora de una visita.
 *
 * Las horas llegan calculadas por el backend y agrupadas acá por día. Todo se
 * muestra en hora de Chile, sin importar dónde esté el comprador.
 *
 * Elegir una hora acá no reserva nada: el panel del costado pide los datos de
 * contacto, y es el backend el que vuelve a comprobar que la hora siga libre.
 */
export function SelectorDeHoras({ slug, horas }: { slug: string; horas: HoraDisponible[] }) {
  const [elegida, setElegida] = useState<HoraDisponible | null>(null);

  if (horas.length === 0) {
    return (
      <p className="rounded-2xl border border-lila/12 bg-superficie p-6 text-sm text-texto-suave">
        No hay horas disponibles en estos días. Prueba con la semana siguiente.
      </p>
    );
  }

  const dias = agruparPorDia(horas);

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start">
      <div className="flex flex-col gap-8">
        {dias.map(([dia, horasDelDia]) => (
          <section key={dia}>
            <h2 className="font-serif text-[22px] text-texto first-letter:uppercase">
              {formatearDiaLargo(horasDelDia[0].inicio)}
            </h2>

            <div className="mt-4 flex flex-wrap gap-2.5">
              {horasDelDia.map((hora) => {
                const seleccionada = elegida?.inicio === hora.inicio;
                return (
                  <button
                    key={hora.inicio}
                    type="button"
                    aria-pressed={seleccionada}
                    onClick={() => setElegida(hora)}
                    className={cn(
                      "h-11 cursor-pointer rounded-xl border px-4 text-sm font-medium transition-colors",
                      seleccionada
                        ? "border-lila bg-violeta/28 text-texto"
                        : "border-lila/18 bg-superficie text-texto-suave hover:border-lila/45",
                    )}
                  >
                    {formatearHora(hora.inicio)}
                  </button>
                );
              })}
            </div>
          </section>
        ))}
      </div>

      <ReservaDeVisita slug={slug} hora={elegida} />
    </div>
  );
}

/** Agrupa las horas por día, conservando el orden en que llegaron. */
function agruparPorDia(horas: HoraDisponible[]): [string, HoraDisponible[]][] {
  const dias = new Map<string, HoraDisponible[]>();

  for (const hora of horas) {
    const dia = diaDe(hora.inicio);
    const delDia = dias.get(dia);
    if (delDia) {
      delDia.push(hora);
    } else {
      dias.set(dia, [hora]);
    }
  }

  return [...dias.entries()];
}
