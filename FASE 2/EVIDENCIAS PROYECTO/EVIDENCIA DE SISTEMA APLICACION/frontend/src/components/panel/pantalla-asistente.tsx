"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { obtenerPreguntas, preguntarAlAsistente } from "@/lib/api/pedidos";
import type { PreguntasDelAsistente } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

import { Cabecera, Error as Aviso, Tarjeta } from "./piezas";

/*
 * El asistente del vendedor.
 *
 * Responde solo sobre la tienda de quien pregunta, y solo las preguntas que
 * sabe. Las ofrece de entrada: un recuadro de texto vacío invita a preguntar
 * cualquier cosa y a recibir «no entendí», que es la peor forma de descubrir
 * para qué sirve algo.
 *
 * Las cifras no las redacta un modelo: las arma el backend con las mismas
 * funciones que pintan el panel, así que el asistente y las pantallas no se
 * pueden contradecir. Por eso cada respuesta puede ofrecer «ver el detalle»
 * y llevar a la sección correspondiente en vez de repetir la tabla acá.
 */

type Turno = { de: "vendedor" | "asistente"; texto: string; seccion?: string | null };

/** A qué ruta del panel lleva cada sección que puede nombrar una respuesta. */
const RUTA: Record<string, string> = {
  ventas: "/panel/ventas",
  pedidos: "/panel/pedidos",
  pronostico: "/panel/pronostico",
  segmentos: "/panel/segmentos",
};

export function PantallaAsistente() {
  const [catalogo, setCatalogo] = useState<PreguntasDelAsistente | null>(null);
  const [turnos, setTurnos] = useState<Turno[]>([]);
  const [borrador, setBorrador] = useState("");
  const [pensando, setPensando] = useState(false);
  const [fallo, setFallo] = useState<string | null>(null);
  const final = useRef<HTMLDivElement>(null);

  useEffect(() => {
    obtenerPreguntas()
      .then(setCatalogo)
      .catch((error: unknown) =>
        setFallo(
          error instanceof Error ? error.message : "No pudimos abrir el asistente.",
        ),
      );
  }, []);

  useEffect(() => {
    final.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turnos]);

  const preguntar = useCallback(async (texto: string) => {
    const limpio = texto.trim();
    if (!limpio) return;

    setTurnos((previos) => [...previos, { de: "vendedor", texto: limpio }]);
    setBorrador("");
    setPensando(true);
    try {
      const respuesta = await preguntarAlAsistente(limpio);
      setTurnos((previos) => [
        ...previos,
        { de: "asistente", texto: respuesta.texto, seccion: respuesta.seccion },
      ]);
      setFallo(null);
    } catch (error) {
      setFallo(
        error instanceof Error ? error.message : "No pudimos responder tu pregunta.",
      );
    } finally {
      setPensando(false);
    }
  }, []);

  const cabecera = (
    <Cabecera
      titulo="Asistente"
      descripcion="Pregúntale por tus ventas, tu stock y tus clientes."
    />
  );

  if (fallo && catalogo === null) {
    return (
      <>
        {cabecera}
        <Aviso mensaje={fallo} />
      </>
    );
  }

  return (
    <>
      {cabecera}

      <Tarjeta className="mt-4">
        <p className="text-xs leading-[1.5] text-pizarra">
          Responde solo sobre tu tienda y solo con datos tuyos. No conversa ni
          opina: las cifras salen de las mismas cuentas que ves en el panel.
        </p>

        {catalogo && turnos.length === 0 && (
          <div className="mt-3.5 flex flex-wrap gap-2">
            {catalogo.preguntas.map((pregunta) => (
              <button
                key={pregunta.intencion}
                type="button"
                onClick={() => preguntar(pregunta.texto)}
                className="cursor-pointer rounded-full border border-arena bg-hueso px-3 py-1.5 text-xs text-marino hover:border-acero hover:text-acero"
              >
                {pregunta.texto}
              </button>
            ))}
          </div>
        )}

        {turnos.length > 0 && (
          <div className="mt-4 flex flex-col gap-3">
            {turnos.map((turno, indice) => (
              <div
                key={`${indice}-${turno.texto.slice(0, 12)}`}
                className={cn(
                  "max-w-[85%] rounded-[12px] px-3.5 py-2.5 text-[13px] leading-[1.55]",
                  turno.de === "vendedor"
                    ? "self-end bg-acero text-white"
                    : "self-start border border-arena bg-hueso text-marino",
                )}
              >
                {turno.texto}
                {turno.seccion && RUTA[turno.seccion] && (
                  <Link
                    href={RUTA[turno.seccion]}
                    className="mt-1.5 block text-xs font-semibold text-acero underline"
                  >
                    Ver el detalle
                  </Link>
                )}
              </div>
            ))}
            {pensando && (
              <p className="self-start text-xs text-pizarra">Buscando en tus datos…</p>
            )}
            <div ref={final} />
          </div>
        )}

        {fallo && (
          <p role="alert" className="mt-3 text-xs text-ambar-hondo">
            {fallo}
          </p>
        )}

        <form
          onSubmit={(evento) => {
            evento.preventDefault();
            preguntar(borrador);
          }}
          className="mt-4 flex gap-2.5"
        >
          <input
            type="text"
            value={borrador}
            disabled={pensando}
            maxLength={catalogo?.largoMaximo ?? 500}
            placeholder="¿Cómo van mis ventas este mes?"
            onChange={(evento) => setBorrador(evento.target.value)}
            aria-label="Tu pregunta"
            className="h-11 w-full rounded-[12px] border border-niebla bg-white px-3 text-[14px] text-marino outline-none focus-visible:border-acero disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={pensando || borrador.trim() === ""}
            className="h-11 shrink-0 cursor-pointer rounded-[12px] bg-acero px-5 text-sm font-semibold text-white hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50"
          >
            Preguntar
          </button>
        </form>
      </Tarjeta>
    </>
  );
}
