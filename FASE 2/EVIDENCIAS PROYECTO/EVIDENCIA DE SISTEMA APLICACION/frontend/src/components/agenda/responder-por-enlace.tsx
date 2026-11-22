"use client";

import { useEffect, useState } from "react";

import { leerCambioPorEnlace, responderPorEnlace, type CambioPorEnlace } from "@/lib/api/agenda";
import { formatearDiaLargo, formatearHora } from "@/lib/formato";

/*
 * Responder un cambio de hora desde el enlace del correo.
 *
 * Muestra qué se está aceptando —la tienda, la hora actual y la propuesta— y
 * espera un clic. La respuesta sugerida por el enlace (aceptar o rechazar) va
 * destacada, pero las dos opciones están a la vista.
 */

function cuando(iso: string) {
  return `${formatearDiaLargo(iso)}, ${formatearHora(iso)}`;
}

export function ResponderCambioPorEnlace({
  firma,
  sugerida,
}: {
  firma: string;
  sugerida: "aceptar" | "rechazar";
}) {
  const [cambio, setCambio] = useState<CambioPorEnlace | null>(null);
  const [error, setError] = useState<string | null>(firma ? null : "El enlace está incompleto.");
  const [listo, setListo] = useState<"aceptado" | "rechazado" | null>(null);
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    if (!firma) return;
    leerCambioPorEnlace(firma).then(setCambio, (e: unknown) =>
      setError(e instanceof Error ? e.message : "El enlace venció o no es válido."),
    );
  }, [firma]);

  async function responder(acepta: boolean) {
    setOcupado(true);
    setError(null);
    try {
      await responderPorEnlace(firma, acepta);
      setListo(acepta ? "aceptado" : "rechazado");
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo responder.");
    } finally {
      setOcupado(false);
    }
  }

  const titulo = "font-jakarta text-[28px] leading-[1.15] font-extrabold tracking-[-0.02em]";

  if (listo) {
    return (
      <div role="status">
        <h1 className={titulo}>{listo === "aceptado" ? "Cambio aceptado" : "Visita cancelada"}</h1>
        <p className="mt-3 text-[15px] leading-[1.55] text-pizarra">
          {listo === "aceptado"
            ? "La visita quedó a la hora nueva. Las dos partes lo ven en su agenda."
            : "Rechazaste el cambio, así que la visita quedó cancelada."}
        </p>
      </div>
    );
  }

  if (error && !cambio) {
    return (
      <div role="alert">
        <h1 className={titulo}>No pudimos abrir el cambio</h1>
        <p className="mt-3 text-[15px] text-pizarra">{error}</p>
      </div>
    );
  }

  if (!cambio) return <p className="text-sm text-pizarra">Cargando…</p>;

  if (cambio.estado !== "pendiente") {
    return (
      <div>
        <h1 className={titulo}>Este cambio ya se respondió</h1>
        <p className="mt-3 text-[15px] text-pizarra">No hay nada más que hacer con este enlace.</p>
      </div>
    );
  }

  const principal =
    "h-12 w-full cursor-pointer rounded-[12px] text-[15px] font-semibold disabled:cursor-not-allowed disabled:opacity-60";

  return (
    <div className="flex flex-col gap-5">
      <div>
        <p className="text-[12px] font-semibold tracking-[0.06em] text-acero uppercase">{cambio.tienda}</p>
        <h1 className={`${titulo} mt-1.5`}>Cambio de hora de una visita</h1>
        <p className="mt-2 text-[15px] text-pizarra">
          {cambio.responde === "tienda"
            ? `${cambio.cliente} pide mover su visita.`
            : "La tienda te propone otra hora para tu visita."}
        </p>
      </div>

      <dl className="flex flex-col gap-3 rounded-xl border border-arena bg-white p-4 text-[14px]">
        <div>
          <dt className="text-[12px] text-pizarra">Hora actual</dt>
          <dd className="font-semibold text-marino first-letter:uppercase">{cuando(cambio.horaActual)}</dd>
        </div>
        <div>
          <dt className="text-[12px] text-pizarra">Hora propuesta</dt>
          <dd className="font-semibold text-acero first-letter:uppercase">{cuando(cambio.horaPropuesta)}</dd>
        </div>
      </dl>

      <div className="flex flex-col gap-2.5">
        <button
          type="button"
          disabled={ocupado}
          onClick={() => responder(true)}
          className={`${principal} ${sugerida === "aceptar" ? "bg-acero text-white hover:bg-acero-hondo" : "border border-arena bg-white text-marino"}`}
        >
          Aceptar la hora propuesta
        </button>
        <button
          type="button"
          disabled={ocupado}
          onClick={() => responder(false)}
          className={`${principal} ${sugerida === "rechazar" ? "bg-marino text-white" : "border border-arena bg-white text-marino"}`}
        >
          Rechazar (la visita se cancela)
        </button>
      </div>

      {error && <p className="text-[13px] text-ambar-hondo">{error}</p>}
    </div>
  );
}
