"use client";

import { useState } from "react";

import type { TemaDeFormulario } from "@/components/campo";
import { escribirALaPlataforma } from "@/lib/api/gestion";
import { cn } from "@/lib/utils";

/*
 * Escribirle a DealCommerce desde la pantalla de inicio de sesión.
 *
 * Aparece solo cuando la tienda de quien intenta entrar la cerró la
 * administración. No hay sesión que usar, así que el mensaje viaja con el
 * correo y la contraseña que la persona acaba de escribir, y el backend los
 * vuelve a verificar. Va dentro del formulario de sesión, por eso no es un
 * <form>: un formulario no puede ir dentro de otro.
 */

const PIEL = {
  claro: {
    caja: "rounded-[12px] border border-arena bg-white p-4",
    texto: "text-[13px] text-pizarra",
    area: "mt-2 w-full rounded-[12px] border border-niebla bg-white p-3 text-[14px] text-marino outline-none focus-visible:border-acero",
    boton:
      "h-11 cursor-pointer rounded-[12px] bg-acero px-5 text-sm font-semibold text-white hover:bg-acero-hondo disabled:cursor-not-allowed disabled:opacity-50",
    secundario: "h-11 cursor-pointer rounded-[12px] border border-niebla px-5 text-sm font-semibold text-acero hover:bg-cielo",
    ok: "rounded-[12px] border border-niebla bg-cielo px-4 py-3 text-[13px] text-acero",
  },
  oscuro: {
    caja: "rounded-xl border border-lila/20 p-4",
    texto: "text-[13px] text-texto-suave",
    area: "mt-2 w-full rounded-xl border border-lila/20 bg-transparent p-3 text-[14px] text-texto outline-none focus-visible:border-lila",
    boton:
      "h-11 cursor-pointer rounded-full bg-violeta px-5 text-sm font-semibold text-white hover:bg-violeta-hover disabled:cursor-not-allowed disabled:opacity-50",
    secundario: "h-11 cursor-pointer rounded-full border border-lila/40 px-5 text-sm font-semibold text-texto hover:bg-violeta/15",
    ok: "rounded-xl border border-lila/25 bg-violeta/10 px-4 py-3 text-[13px] text-texto",
  },
} as const;

export function EscribirADealCommerce({
  email,
  password,
  tema,
}: {
  email: string;
  password: string;
  tema: TemaDeFormulario;
}) {
  const piel = PIEL[tema];
  const [abierto, setAbierto] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [respuesta, setRespuesta] = useState<string | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  async function enviar() {
    setEnviando(true);
    setFallo(null);
    try {
      setRespuesta(await escribirALaPlataforma(email, password, mensaje.trim()));
    } catch (error) {
      setFallo(error instanceof Error ? error.message : "No pudimos enviar tu mensaje.");
    } finally {
      setEnviando(false);
    }
  }

  if (respuesta) {
    return (
      <p role="status" className={piel.ok}>
        {respuesta}
      </p>
    );
  }

  if (!abierto) {
    return (
      <button type="button" className={piel.boton} onClick={() => setAbierto(true)}>
        Escribir a DealCommerce
      </button>
    );
  }

  return (
    <div className={piel.caja}>
      <label htmlFor="mensaje-a-dealcommerce" className={cn(piel.texto, "font-semibold")}>
        Tu mensaje para la administración
      </label>
      <textarea
        id="mensaje-a-dealcommerce"
        rows={4}
        maxLength={2000}
        value={mensaje}
        onChange={(e) => setMensaje(e.target.value)}
        placeholder="Cuéntanos por qué quieres reabrir tu tienda o qué necesitas."
        className={piel.area}
      />
      <p className={cn(piel.texto, "mt-1")}>Te respondemos al correo de tu cuenta: {email}</p>
      {fallo && (
        <p role="alert" className={cn(piel.texto, "mt-2 font-semibold")}>
          {fallo}
        </p>
      )}
      <div className="mt-3 flex flex-wrap gap-2">
        <button type="button" className={piel.boton} disabled={enviando || mensaje.trim().length < 5} onClick={enviar}>
          {enviando ? "Enviando…" : "Enviar mensaje"}
        </button>
        <button type="button" className={piel.secundario} onClick={() => setAbierto(false)}>
          Cancelar
        </button>
      </div>
    </div>
  );
}
