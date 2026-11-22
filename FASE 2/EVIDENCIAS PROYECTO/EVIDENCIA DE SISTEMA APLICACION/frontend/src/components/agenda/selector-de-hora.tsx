"use client";

import { useEffect, useMemo, useState } from "react";

import { DIAS_POR_PANTALLA, obtenerAgenda } from "@/lib/api/agenda";
import { diaDe, formatearDiaLargo, formatearHora, sumarDias } from "@/lib/formato";
import type { AgendaPublica } from "@/lib/tipos";
import { cn } from "@/lib/utils";

/*
 * Elegir otra hora para una visita: lo usan «Mis citas» del cliente y la
 * agenda del panel, para proponer un cambio.
 *
 * Las horas son las mismas que ofrece la agenda pública de la tienda, de a una
 * semana: el backend vuelve a validar la que se elija, así que una hora que
 * se ocupó mientras tanto se rechaza allá y no acá.
 *
 * El aspecto cambia con `tema`: la vitrina es oscura y lleva los colores de la
 * tienda; el panel es claro y lleva los de DealCommerce.
 */

const TEMAS = {
  tienda: {
    marco: "rounded-2xl border border-lila/16 bg-superficie p-4",
    titulo: "text-[13px] font-semibold text-texto",
    suave: "text-[12.5px] text-texto-suave",
    navegar:
      "h-9 cursor-pointer rounded-full border border-lila/30 px-3 text-[12.5px] text-texto hover:bg-violeta/15 disabled:cursor-not-allowed disabled:opacity-40",
    dia: "text-[13px] font-semibold text-texto first-letter:uppercase",
    hora: "h-9 cursor-pointer rounded-full border border-lila/25 px-3 text-[13px] text-texto tabular-nums hover:border-lila",
    horaElegida: "border-violeta bg-violeta text-white hover:border-violeta",
    principal:
      "h-11 cursor-pointer rounded-full bg-violeta px-5 text-sm font-semibold text-white hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50",
    secundario: "h-11 cursor-pointer rounded-full border border-lila/30 px-5 text-sm text-texto hover:bg-violeta/15",
  },
  panel: {
    marco: "rounded-xl border border-arena bg-hueso p-4",
    titulo: "text-[13px] font-semibold text-marino",
    suave: "text-[12.5px] text-pizarra",
    navegar:
      "h-9 cursor-pointer rounded-lg border border-arena bg-white px-3 text-[12.5px] text-marino hover:border-niebla disabled:cursor-not-allowed disabled:opacity-40",
    dia: "text-[13px] font-semibold text-marino first-letter:uppercase",
    hora: "h-9 cursor-pointer rounded-lg border border-arena bg-white px-3 text-[13px] text-marino tabular-nums hover:border-acero",
    horaElegida: "border-acero bg-acero text-white hover:border-acero",
    principal:
      "h-10 cursor-pointer rounded-[10px] bg-acero px-4 text-[13px] font-semibold text-white hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50",
    secundario:
      "h-10 cursor-pointer rounded-[10px] border border-arena bg-white px-4 text-[13px] font-semibold text-pizarra hover:border-niebla",
  },
} as const;

export function SelectorDeHora({
  slug,
  horaActual,
  tema,
  ocupado = false,
  onElegir,
  onCancelar,
  textoBoton = "Proponer esta hora",
}: {
  slug: string;
  /** La hora que tiene hoy la visita: no se ofrece de nuevo. */
  horaActual: string;
  tema: keyof typeof TEMAS;
  ocupado?: boolean;
  onElegir: (inicio: string) => void;
  onCancelar: () => void;
  textoBoton?: string;
}) {
  const estilo = TEMAS[tema];
  const [desde, setDesde] = useState<string | undefined>(undefined);
  const [agenda, setAgenda] = useState<AgendaPublica | null | "error">(null);
  const [elegida, setElegida] = useState<string | null>(null);

  useEffect(() => {
    let vigente = true;
    obtenerAgenda(slug, { desde, dias: DIAS_POR_PANTALLA }).then((respuesta) => {
      if (vigente) setAgenda(respuesta ?? "error");
    });
    return () => {
      vigente = false;
    };
  }, [slug, desde]);

  const porDia = useMemo(() => {
    if (!agenda || agenda === "error") return [];
    const grupos = new Map<string, string[]>();
    for (const hora of agenda.horas) {
      if (hora.inicio === horaActual || new Date(hora.inicio).getTime() === new Date(horaActual).getTime()) {
        continue;
      }
      const dia = diaDe(hora.inicio);
      grupos.set(dia, [...(grupos.get(dia) ?? []), hora.inicio]);
    }
    return [...grupos.entries()];
  }, [agenda, horaActual]);

  if (agenda === null) return <p className={cn(estilo.marco, estilo.suave)}>Buscando horas libres…</p>;
  if (agenda === "error") {
    return <p className={cn(estilo.marco, estilo.suave)}>No pudimos cargar las horas de la tienda.</p>;
  }

  const puedeAtras = agenda.rango.desde > agenda.ventana.desde;
  const puedeAdelante = agenda.rango.hasta < agenda.ventana.hasta;

  return (
    <div className={cn(estilo.marco, "flex flex-col gap-4")}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className={estilo.titulo}>Elige la hora nueva</p>
        <div className="flex gap-2">
          <button
            type="button"
            className={estilo.navegar}
            disabled={!puedeAtras}
            onClick={() => setDesde(sumarDias(agenda.rango.desde, -DIAS_POR_PANTALLA))}
          >
            ← Semana anterior
          </button>
          <button
            type="button"
            className={estilo.navegar}
            disabled={!puedeAdelante}
            onClick={() => setDesde(sumarDias(agenda.rango.hasta, 1))}
          >
            Semana siguiente →
          </button>
        </div>
      </div>

      {porDia.length === 0 ? (
        <p className={estilo.suave}>No quedan horas libres esta semana. Prueba con la siguiente.</p>
      ) : (
        <div className="flex max-h-[320px] flex-col gap-3.5 overflow-y-auto pr-1">
          {porDia.map(([dia, horas]) => (
            <div key={dia} className="flex flex-col gap-2">
              <p className={estilo.dia}>{formatearDiaLargo(horas[0])}</p>
              <div className="flex flex-wrap gap-2" role="radiogroup" aria-label={formatearDiaLargo(horas[0])}>
                {horas.map((inicio) => (
                  <button
                    key={inicio}
                    type="button"
                    role="radio"
                    aria-checked={elegida === inicio}
                    onClick={() => setElegida(inicio)}
                    className={cn(estilo.hora, elegida === inicio && estilo.horaElegida)}
                  >
                    {formatearHora(inicio)}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2.5">
        <button
          type="button"
          className={estilo.principal}
          disabled={!elegida || ocupado}
          onClick={() => elegida && onElegir(elegida)}
        >
          {ocupado ? "Enviando…" : textoBoton}
        </button>
        <button type="button" className={estilo.secundario} onClick={onCancelar}>
          Cancelar
        </button>
      </div>
    </div>
  );
}
