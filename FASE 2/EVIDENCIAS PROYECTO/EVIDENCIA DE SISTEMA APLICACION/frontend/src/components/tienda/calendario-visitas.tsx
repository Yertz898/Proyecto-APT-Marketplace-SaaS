"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { diaDe, formatearHora } from "@/lib/formato";
import type { AgendaPublica, HoraDisponible } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { ReservaDeVisita } from "./reserva-visita";

/*
 * La agenda de visitas como calendario.
 *
 * Arriba, una tira con los próximos días y cuántas horas libres tiene cada uno;
 * «Otra fecha» abre el mes completo en una ventana. Al elegir un día se ven sus
 * horas, y al elegir una hora se piden los datos al costado.
 *
 * Las horas llegan del backend ya filtradas: no aparecen las que una visita
 * confirmada ya tomó. Una solicitud que todavía no confirma la tienda no
 * esconde la hora; la esconde la confirmación.
 *
 * Las fechas se manejan como texto aaaa-mm-dd y se suman en UTC: así un cambio
 * de horario en Chile nunca hace saltar ni repetir un día.
 */

const NOMBRES_DIA = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"];
const MESES = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];
const DIAS_EN_LA_TIRA = 7;

function aFecha(texto: string): Date {
  const [a, m, d] = texto.split("-").map(Number);
  return new Date(Date.UTC(a, m - 1, d));
}

function aTexto(fecha: Date): string {
  return fecha.toISOString().slice(0, 10);
}

function sumar(texto: string, dias: number): string {
  const fecha = aFecha(texto);
  fecha.setUTCDate(fecha.getUTCDate() + dias);
  return aTexto(fecha);
}

/** 0 es lunes, como en la agenda de la tienda. */
function diaDeLaSemana(texto: string): number {
  return (aFecha(texto).getUTCDay() + 6) % 7;
}

function etiquetaCorta(texto: string): { dia: string; numero: number; mes: string } {
  const fecha = aFecha(texto);
  return {
    dia: NOMBRES_DIA[diaDeLaSemana(texto)],
    numero: fecha.getUTCDate(),
    mes: MESES[fecha.getUTCMonth()].slice(0, 3),
  };
}

function etiquetaLarga(texto: string): string {
  const fecha = aFecha(texto);
  const nombres = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"];
  return `${nombres[diaDeLaSemana(texto)]} ${fecha.getUTCDate()} de ${MESES[fecha.getUTCMonth()]}`;
}

export function CalendarioDeVisitas({
  slug,
  agenda,
  diaPedido,
}: {
  slug: string;
  agenda: AgendaPublica;
  diaPedido?: string;
}) {
  const router = useRouter();
  const ruta = usePathname();

  // Las horas libres de cada día del rango que trajo el servidor.
  const porDia = useMemo(() => {
    const mapa = new Map<string, HoraDisponible[]>();
    for (const hora of agenda.horas) {
      const dia = diaDe(hora.inicio);
      mapa.set(dia, [...(mapa.get(dia) ?? []), hora]);
    }
    return mapa;
  }, [agenda.horas]);

  const primerDiaConHoras = agenda.horas.length ? diaDe(agenda.horas[0].inicio) : agenda.rango.desde;
  const diaInicial = diaPedido && diaPedido >= agenda.ventana.desde ? diaPedido : primerDiaConHoras;

  const [dia, setDia] = useState(diaInicial);
  const [hora, setHora] = useState<HoraDisponible | null>(null);
  const [mesAbierto, setMesAbierto] = useState(false);

  function elegirDia(nuevo: string) {
    setHora(null);
    setMesAbierto(false);
    // Un día fuera de lo que trajo el servidor se pide de nuevo desde ese día.
    if (nuevo < agenda.rango.desde || nuevo > agenda.rango.hasta) {
      router.push(`${ruta}?dia=${nuevo}`);
      return;
    }
    setDia(nuevo);
  }

  // La tira parte en el primer día del rango y no se mueve al elegir dentro de
  // ella; si el día elegido queda fuera, parte en ese día.
  const ancla = dia < sumar(agenda.rango.desde, DIAS_EN_LA_TIRA) ? agenda.rango.desde : dia;
  const tira = Array.from({ length: DIAS_EN_LA_TIRA }, (_, i) => sumar(ancla, i)).filter(
    (d) => d <= agenda.ventana.hasta,
  );
  const horasDelDia = porDia.get(dia) ?? [];

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start">
      <div>
        <div className="flex items-center justify-between gap-3">
          <p className="font-serif text-[22px] text-texto first-letter:uppercase">
            {MESES[aFecha(dia).getUTCMonth()]} {aFecha(dia).getUTCFullYear()}
          </p>
          <button
            type="button"
            onClick={() => setMesAbierto(true)}
            className="inline-flex h-10 cursor-pointer items-center gap-2 rounded-full border border-lila/30 px-4 text-[13px] font-semibold text-texto transition-colors hover:bg-violeta/15"
          >
            <IconoCalendario />
            Otra fecha
          </button>
        </div>

        <div className="mt-4 grid grid-cols-4 gap-2 sm:grid-cols-7">
          {tira.map((d) => {
            const etiqueta = etiquetaCorta(d);
            const libres = porDia.get(d)?.length ?? 0;
            const elegido = d === dia;
            return (
              <button
                key={d}
                type="button"
                onClick={() => elegirDia(d)}
                aria-pressed={elegido}
                className={cn(
                  "flex cursor-pointer flex-col items-center rounded-2xl border px-2 py-3 transition-colors",
                  elegido
                    ? "border-violeta bg-violeta text-white"
                    : libres > 0
                      ? "border-lila/20 bg-superficie text-texto hover:border-lila/50"
                      : "border-lila/10 bg-transparent text-texto-apagado",
                )}
              >
                <span className="text-[12px] font-semibold uppercase">{etiqueta.dia}</span>
                <span className="font-serif text-[26px] leading-none">{etiqueta.numero}</span>
                <span className={cn("mt-1 text-[11px]", elegido ? "text-white/85" : "text-texto-suave")}>
                  {libres > 0 ? `${libres} ${libres === 1 ? "hora" : "horas"}` : "Sin horas"}
                </span>
              </button>
            );
          })}
        </div>

        <section className="mt-8">
          <h2 className="font-serif text-[22px] text-texto first-letter:uppercase">{etiquetaLarga(dia)}</h2>
          {horasDelDia.length === 0 ? (
            <p className="mt-3 rounded-2xl border border-lila/12 bg-superficie p-5 text-sm text-texto-suave">
              No quedan horas libres este día. Elige otro en la tira o en «Otra fecha».
            </p>
          ) : (
            <div className="mt-4 grid grid-cols-3 gap-2.5 sm:grid-cols-4 md:grid-cols-5">
              {horasDelDia.map((h) => {
                const elegida = hora?.inicio === h.inicio;
                return (
                  <button
                    key={h.inicio}
                    type="button"
                    aria-pressed={elegida}
                    onClick={() => setHora(h)}
                    className={cn(
                      "h-12 cursor-pointer rounded-xl border text-sm font-semibold transition-colors",
                      elegida
                        ? "border-violeta bg-violeta text-white"
                        : "border-lila/20 bg-superficie text-texto hover:border-lila/50",
                    )}
                  >
                    {formatearHora(h.inicio)}
                  </button>
                );
              })}
            </div>
          )}
        </section>
      </div>

      <ReservaDeVisita slug={slug} hora={hora} />

      {mesAbierto && (
        <SelectorDeMes
          elegido={dia}
          ventana={agenda.ventana}
          rango={agenda.rango}
          conHoras={porDia}
          onElegir={elegirDia}
          onCerrar={() => setMesAbierto(false)}
        />
      )}
    </div>
  );
}

/** El mes completo en una ventana, para saltar a cualquier fecha que acepte la tienda. */
function SelectorDeMes({
  elegido,
  ventana,
  rango,
  conHoras,
  onElegir,
  onCerrar,
}: {
  elegido: string;
  ventana: AgendaPublica["ventana"];
  rango: AgendaPublica["rango"];
  conHoras: Map<string, HoraDisponible[]>;
  onElegir: (dia: string) => void;
  onCerrar: () => void;
}) {
  const [mes, setMes] = useState(elegido.slice(0, 7) + "-01");

  useEffect(() => {
    const alPresionar = (evento: KeyboardEvent) => evento.key === "Escape" && onCerrar();
    window.addEventListener("keydown", alPresionar);
    return () => window.removeEventListener("keydown", alPresionar);
  }, [onCerrar]);

  const fecha = aFecha(mes);
  const diasDelMes = new Date(Date.UTC(fecha.getUTCFullYear(), fecha.getUTCMonth() + 1, 0)).getUTCDate();
  const vacios = diaDeLaSemana(mes);
  const mesAnterior = aTexto(new Date(Date.UTC(fecha.getUTCFullYear(), fecha.getUTCMonth() - 1, 1)));
  const mesSiguiente = aTexto(new Date(Date.UTC(fecha.getUTCFullYear(), fecha.getUTCMonth() + 1, 1)));
  const puedeAtras = mesAnterior.slice(0, 7) >= ventana.desde.slice(0, 7);
  const puedeAdelante = mesSiguiente.slice(0, 7) <= ventana.hasta.slice(0, 7);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Elegir fecha"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onCerrar}
    >
      <div
        className="w-full max-w-[380px] rounded-3xl border border-lila/20 bg-superficie p-5 shadow-2xl"
        onClick={(evento) => evento.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <button
            type="button"
            aria-label="Mes anterior"
            disabled={!puedeAtras}
            onClick={() => setMes(mesAnterior)}
            className="flex size-9 cursor-pointer items-center justify-center rounded-full text-[20px] text-texto hover:bg-violeta/15 disabled:cursor-not-allowed disabled:opacity-30"
          >
            ‹
          </button>
          <p className="font-serif text-[22px] text-texto first-letter:uppercase">
            {MESES[fecha.getUTCMonth()]} {fecha.getUTCFullYear()}
          </p>
          <button
            type="button"
            aria-label="Mes siguiente"
            disabled={!puedeAdelante}
            onClick={() => setMes(mesSiguiente)}
            className="flex size-9 cursor-pointer items-center justify-center rounded-full text-[20px] text-texto hover:bg-violeta/15 disabled:cursor-not-allowed disabled:opacity-30"
          >
            ›
          </button>
        </div>

        <div className="mt-4 grid grid-cols-7 gap-1 text-center">
          {NOMBRES_DIA.map((nombre) => (
            <span key={nombre} className="py-1 text-[11px] font-semibold text-texto-suave uppercase">
              {nombre}
            </span>
          ))}
          {Array.from({ length: vacios }, (_, i) => (
            <span key={`vacio-${i}`} />
          ))}
          {Array.from({ length: diasDelMes }, (_, i) => {
            const d = sumar(mes, i);
            const dentro = d >= ventana.desde && d <= ventana.hasta;
            const conocido = d >= rango.desde && d <= rango.hasta;
            const libres = conHoras.get(d)?.length ?? 0;
            // Dentro de lo que ya se sabe, un día sin horas no se ofrece. Más
            // allá, se puede elegir y la página trae sus horas.
            const habilitado = dentro && (!conocido || libres > 0);
            const elegidoAhora = d === elegido;
            return (
              <button
                key={d}
                type="button"
                disabled={!habilitado}
                onClick={() => onElegir(d)}
                className={cn(
                  "relative flex aspect-square cursor-pointer items-center justify-center rounded-full text-[14px] transition-colors disabled:cursor-not-allowed",
                  elegidoAhora
                    ? "bg-violeta font-semibold text-white"
                    : habilitado
                      ? "text-texto hover:bg-violeta/20"
                      : "text-texto-apagado/50",
                )}
              >
                {i + 1}
                {libres > 0 && !elegidoAhora && (
                  <span className="absolute bottom-1.5 size-1 rounded-full bg-oro" aria-hidden="true" />
                )}
              </button>
            );
          })}
        </div>

        <p className="mt-4 flex items-center gap-2 text-[12px] text-texto-suave">
          <span className="size-1.5 rounded-full bg-oro" aria-hidden="true" /> Días con horas libres
        </p>
        <button
          type="button"
          onClick={onCerrar}
          className="mt-4 h-11 w-full cursor-pointer rounded-full border border-lila/30 text-sm font-semibold text-texto hover:bg-violeta/15"
        >
          Cerrar
        </button>
      </div>
    </div>
  );
}

function IconoCalendario() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M3 10h18M8 3v4M16 3v4" />
    </svg>
  );
}
