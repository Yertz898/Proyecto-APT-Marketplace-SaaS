"use client";

import { useState } from "react";

import { diaDe, formatearDiaLargo, formatearHora } from "@/lib/formato";
import type { HoraDisponible } from "@/lib/tipos";
import { cn } from "@/lib/utils";

/*
 * Selección de la hora de una visita.
 *
 * Las horas llegan calculadas por el backend y agrupadas acá por día. Todo se
 * muestra en hora de Chile, sin importar dónde esté el comprador.
 *
 * Reservar exige que el comprador tenga sesión, y eso todavía no existe: por
 * ahora se puede elegir la hora, pero el paso siguiente queda bloqueado con el
 * motivo a la vista.
 */
export function SelectorDeHoras({ horas }: { horas: HoraDisponible[] }) {
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

      <aside className="rounded-2xl border border-lila/16 p-5">
        <h2 className="text-[13px] font-semibold text-texto">Tu visita</h2>

        {elegida ? (
          <>
            <p className="mt-3 text-sm text-texto first-letter:uppercase">
              {formatearDiaLargo(elegida.inicio)}
            </p>
            <p className="text-sm text-texto-suave">
              {formatearHora(elegida.inicio)} a {formatearHora(elegida.fin)}
            </p>

            {elegida.nombreBloque && (
              <p className="mt-2 text-[13px] text-lila">{elegida.nombreBloque}</p>
            )}

            <p className="mt-3 text-xs text-texto-suave">
              {elegida.confirmacionAutomatica
                ? "Se confirma al instante."
                : "Queda pendiente hasta que la tienda la acepte."}
            </p>
          </>
        ) : (
          <p className="mt-3 text-[13px] text-texto-suave">Elige una hora para continuar.</p>
        )}

        <button
          type="button"
          disabled
          data-pendiente="reservar-visita"
          className="mt-5 h-12 w-full rounded-full bg-violeta text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          Continuar
        </button>

        <p className="mt-3 text-xs leading-[1.5] text-texto-suave">
          Para reservar hay que iniciar sesión, y esa parte todavía no está construida.
        </p>
      </aside>
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
