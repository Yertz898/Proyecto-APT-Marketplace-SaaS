"use client";

import type { InputHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

/*
 * Controles de formulario que comparten las pantallas de gestión.
 *
 * Mismo alto, borde y foco que el formulario de producto, para que la cuenta,
 * el equipo o la agenda no parezcan de otra aplicación.
 */

export const CLASE_ENTRADA =
  "mt-2 h-12 w-full rounded-[12px] border border-niebla bg-white px-3 text-base text-marino outline-none focus-visible:border-acero disabled:opacity-60";

export function Campo({
  id,
  etiqueta,
  error,
  ayuda,
  ...resto
}: InputHTMLAttributes<HTMLInputElement> & {
  id: string;
  etiqueta: string;
  error?: string | null;
  ayuda?: string;
}) {
  return (
    <div>
      <label htmlFor={id} className="text-[13px] font-semibold text-marino">
        {etiqueta}
      </label>
      <input id={id} aria-invalid={Boolean(error)} className={CLASE_ENTRADA} {...resto} />
      {ayuda && !error && <p className="mt-1.5 text-xs text-pizarra">{ayuda}</p>}
      {error && <p className="mt-1.5 text-xs font-medium text-ambar-hondo">{error}</p>}
    </div>
  );
}

export function Boton({
  children,
  variante = "principal",
  className,
  ...resto
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variante?: "principal" | "secundario" | "peligro";
}) {
  return (
    <button
      type="button"
      className={cn(
        "h-11 cursor-pointer rounded-[12px] px-5 text-[14px] font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50",
        variante === "principal" && "bg-acero text-white hover:bg-acero-hondo",
        variante === "secundario" && "border border-niebla bg-white text-acero hover:bg-cielo",
        variante === "peligro" && "bg-[#b42318] text-white hover:bg-[#912018]",
        className,
      )}
      {...resto}
    >
      {children}
    </button>
  );
}

/** Un aviso breve después de guardar: verde si salió, ámbar si no. */
export function Aviso({ tipo, children }: { tipo: "ok" | "error"; children: ReactNode }) {
  return (
    <p
      role={tipo === "error" ? "alert" : "status"}
      className={cn(
        "mt-3 rounded-[12px] px-4 py-3 text-[13px]",
        tipo === "ok" ? "border border-niebla bg-cielo text-acero" : "border border-ambar bg-trigo text-marino",
      )}
    >
      {children}
    </p>
  );
}

export function mensajeDe(error: unknown): string {
  return error instanceof Error ? error.message : "No se pudo completar la operación.";
}
