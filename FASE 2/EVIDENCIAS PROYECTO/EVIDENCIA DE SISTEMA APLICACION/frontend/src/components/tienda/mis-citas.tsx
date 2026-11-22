"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { SelectorDeHora } from "@/components/agenda/selector-de-hora";
import { useSesion } from "@/components/sesion/usar-sesion";
import { cancelarMiVisita, obtenerMisVisitas, proponerOtraHora, responderOtraHora } from "@/lib/api/agenda";
import { formatearDiaLargo, formatearHora } from "@/lib/formato";
import type { MiVisita } from "@/lib/tipos";
import { cn } from "@/lib/utils";

/*
 * «Mis citas»: las visitas que el comprador agendó en esta tienda.
 *
 * Desde acá puede pedir otra hora (la tienda la acepta o la rechaza; si la
 * rechaza, la visita se cancela), responder la hora que le propuso la tienda,
 * o cancelar. Todo lo valida el backend: la pantalla solo ofrece los botones
 * que corresponden al estado de cada visita.
 */

const COLOR_DEL_ESTADO: Record<string, string> = {
  solicitada: "border-oro/40 bg-oro/10 text-oro",
  confirmada: "border-lila/40 bg-violeta/15 text-lila-claro",
  cancelada: "border-lila/15 text-texto-suave",
  rechazada: "border-lila/15 text-texto-suave",
  asistida: "border-lila/15 text-texto-suave",
  no_asistio: "border-lila/15 text-texto-suave",
};

function cuando(iso: string) {
  return `${formatearDiaLargo(iso)}, ${formatearHora(iso)}`;
}

export function MisCitas({ slug }: { slug: string }) {
  const { sesion, hidratado } = useSesion();
  const [visitas, setVisitas] = useState<MiVisita[] | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  const cargar = useCallback(() => {
    obtenerMisVisitas(slug)
      .then((suyas) => {
        setVisitas(suyas);
        setFallo(null);
      })
      .catch((error: unknown) => setFallo(error instanceof Error ? error.message : "No pudimos cargar tus citas."));
  }, [slug]);

  useEffect(() => {
    if (sesion?.usuario.rol === "comprador") cargar();
  }, [sesion, cargar]);

  if (!hidratado) return <p className="text-sm text-texto-suave">Cargando…</p>;

  if (!sesion || sesion.usuario.rol !== "comprador") {
    return (
      <div className="rounded-2xl border border-lila/16 p-6">
        <p className="text-sm text-texto">Inicia sesión con tu cuenta de cliente para ver tus citas.</p>
        <Link
          href={`/t/${slug}/entrar?volver=${encodeURIComponent(`/t/${slug}/cuenta/citas`)}`}
          className="mt-4 inline-flex h-11 items-center rounded-full bg-violeta px-5 text-sm font-semibold text-white hover:bg-violeta-hover"
        >
          Iniciar sesión
        </Link>
      </div>
    );
  }

  if (fallo) {
    return (
      <div role="alert" className="rounded-2xl border border-oro/35 bg-oro/8 p-5 text-sm text-texto">
        {fallo}
        <button type="button" onClick={cargar} className="ml-3 cursor-pointer text-lila underline">
          Reintentar
        </button>
      </div>
    );
  }

  if (visitas === null) return <p className="text-sm text-texto-suave">Cargando tus citas…</p>;

  if (visitas.length === 0) {
    return (
      <div className="rounded-2xl border border-lila/16 p-6">
        <p className="text-sm text-texto">Todavía no tienes citas en esta tienda.</p>
        <Link
          href={`/t/${slug}/agenda`}
          className="mt-4 inline-flex h-11 items-center rounded-full bg-violeta px-5 text-sm font-semibold text-white hover:bg-violeta-hover"
        >
          Agendar una visita
        </Link>
      </div>
    );
  }

  return (
    <ul className="flex list-none flex-col gap-4 p-0">
      {visitas.map((visita) => (
        <TarjetaDeCita
          key={visita.id}
          slug={slug}
          visita={visita}
          onCambio={(nueva) => setVisitas((previas) => (previas ?? []).map((v) => (v.id === nueva.id ? nueva : v)))}
        />
      ))}
    </ul>
  );
}

function TarjetaDeCita({
  slug,
  visita,
  onCambio,
}: {
  slug: string;
  visita: MiVisita;
  onCambio: (visita: MiVisita) => void;
}) {
  const [eligiendo, setEligiendo] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cambio = visita.cambioPendiente;

  async function hacer(accion: () => Promise<MiVisita>) {
    setOcupado(true);
    setError(null);
    try {
      onCambio(await accion());
      setEligiendo(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo completar la acción.");
    } finally {
      setOcupado(false);
    }
  }

  return (
    <li className={cn("rounded-2xl border border-lila/16 p-5", !visita.vigente && "opacity-70")}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[15px] font-semibold text-texto first-letter:uppercase">{cuando(visita.inicio)}</p>
          {visita.motivo && <p className="mt-1 text-[13px] text-texto-suave">{visita.motivo}</p>}
          {visita.motivoRechazo && (
            <p className="mt-1 text-[13px] text-texto-suave">Motivo: {visita.motivoRechazo}</p>
          )}
        </div>
        <span
          className={cn(
            "rounded-full border px-2.5 py-0.5 text-[11.5px] font-semibold",
            COLOR_DEL_ESTADO[visita.estado] ?? "border-lila/15 text-texto-suave",
          )}
        >
          {visita.estadoNombre}
        </span>
      </div>

      {cambio && cambio.propuestoPor === "comprador" && (
        <p className="mt-4 rounded-xl border border-lila/25 bg-violeta/10 px-4 py-3 text-[13px] text-texto">
          Pediste cambiarla al <b className="first-letter:uppercase">{cuando(cambio.inicio)}</b>. Esperando que la
          tienda responda.
        </p>
      )}

      {cambio && cambio.propuestoPor === "tienda" && (
        <div className="mt-4 rounded-xl border border-oro/35 bg-oro/8 px-4 py-3.5">
          <p className="text-[13px] text-texto">
            La tienda te propone cambiarla al <b>{cuando(cambio.inicio)}</b>. Si la rechazas, la visita se cancela.
          </p>
          <div className="mt-3 flex flex-wrap gap-2.5">
            <button
              type="button"
              disabled={ocupado}
              onClick={() => hacer(() => responderOtraHora(slug, visita.id, true))}
              className="h-10 cursor-pointer rounded-full bg-violeta px-4 text-[13px] font-semibold text-white hover:bg-violeta-hover disabled:opacity-50"
            >
              Aceptar la nueva hora
            </button>
            <button
              type="button"
              disabled={ocupado}
              onClick={() => {
                if (window.confirm("Si rechazas la nueva hora, la visita se cancela. ¿Seguir?")) {
                  hacer(() => responderOtraHora(slug, visita.id, false));
                }
              }}
              className="h-10 cursor-pointer rounded-full border border-lila/30 px-4 text-[13px] text-texto hover:bg-violeta/15 disabled:opacity-50"
            >
              Rechazar
            </button>
          </div>
        </div>
      )}

      {visita.vigente && !cambio && !eligiendo && (
        <div className="mt-4 flex flex-wrap gap-2.5">
          <button
            type="button"
            onClick={() => setEligiendo(true)}
            className="h-10 cursor-pointer rounded-full border border-lila/40 px-4 text-[13px] font-medium text-texto hover:bg-violeta/15"
          >
            Reagendar
          </button>
          <button
            type="button"
            disabled={ocupado}
            onClick={() => {
              if (window.confirm("¿Cancelar esta visita?")) hacer(() => cancelarMiVisita(slug, visita.id));
            }}
            className="h-10 cursor-pointer rounded-full px-4 text-[13px] text-texto-suave hover:text-texto disabled:opacity-50"
          >
            Cancelar visita
          </button>
        </div>
      )}

      {eligiendo && (
        <div className="mt-4">
          <SelectorDeHora
            slug={slug}
            horaActual={visita.inicio}
            tema="tienda"
            ocupado={ocupado}
            textoBoton="Pedir esta hora"
            onElegir={(inicio) => hacer(() => proponerOtraHora(slug, visita.id, inicio))}
            onCancelar={() => setEligiendo(false)}
          />
          <p className="mt-2 text-xs text-texto-suave">
            La tienda tiene que aceptar el cambio. Si no puede, la visita se cancela y te avisamos acá.
          </p>
        </div>
      )}

      {error && <p className="mt-3 text-[13px] text-oro">{error}</p>}
    </li>
  );
}
