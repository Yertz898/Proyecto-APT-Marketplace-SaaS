import Link from "next/link";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { NOMBRE_DEL_PLAN } from "./secciones";
import type { Plan } from "@/lib/tipos";

/*
 * Las piezas que repite cada sección del panel.
 *
 * Están juntas para que las quince pantallas se vean como una sola aplicación
 * y no como quince. Si mañana cambia el espaciado de un encabezado, cambia en
 * todas a la vez.
 */

export function Cabecera({
  titulo,
  descripcion,
  acciones,
}: {
  titulo: string;
  descripcion?: string;
  acciones?: ReactNode;
}) {
  return (
    <div className="mb-7 flex flex-wrap items-start justify-between gap-4">
      <div className="max-w-[620px]">
        <h1 className="font-jakarta text-[28px] leading-[1.15] font-extrabold tracking-[-0.02em] text-marino">
          {titulo}
        </h1>
        {descripcion && <p className="mt-2 text-[15px] leading-[1.5] text-pizarra">{descripcion}</p>}
      </div>
      {acciones && <div className="flex flex-wrap gap-2.5">{acciones}</div>}
    </div>
  );
}

export function Tarjeta({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <section className={cn("rounded-[14px] border border-arena bg-white p-6", className)}>
      {children}
    </section>
  );
}

/**
 * Franja de demostración.
 *
 * Va en toda pantalla cuyos datos son de ejemplo. Es una regla del proyecto:
 * ninguna cifra sintética puede pasar por real.
 */
export function FranjaDeDemostracion({ detalle }: { detalle?: string }) {
  return (
    <p
      role="status"
      className="mb-6 flex flex-wrap items-center gap-2 rounded-[12px] border border-ambar bg-trigo px-4 py-3 text-[13px] text-marino"
    >
      <span className="size-[7px] shrink-0 rounded-full bg-ambar" />
      <span className="font-semibold">Demostración:</span>
      <span>los datos de esta sección son de ejemplo.</span>
      {detalle && <span className="text-pizarra">{detalle}</span>}
    </p>
  );
}

/** Lo que se muestra cuando una acción simulada "ocurre". */
export function AvisoSimulado() {
  return (
    <p role="status" className="mt-4 text-[13px] text-pizarra">
      En demostración: este cambio no se guarda.
    </p>
  );
}

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return (
    <p role="status" className="py-14 text-center text-sm text-pizarra">
      {texto}
    </p>
  );
}

/** Vacío con una salida: un vacío sin acción deja a la persona detenida. */
export function Vacio({
  titulo,
  detalle,
  accion,
}: {
  titulo: string;
  detalle?: string;
  accion?: { href: string; etiqueta: string };
}) {
  return (
    <div className="rounded-[14px] border border-dashed border-arena-honda bg-white px-6 py-12 text-center">
      <p className="font-jakarta text-[17px] font-bold text-marino">{titulo}</p>
      {detalle && <p className="mx-auto mt-2 max-w-[420px] text-[14px] text-pizarra">{detalle}</p>}
      {accion && (
        <Link
          href={accion.href}
          className="mt-5 inline-flex h-11 items-center rounded-[12px] bg-acero px-5 text-[14px] font-semibold text-white no-underline hover:bg-acero-hondo hover:no-underline"
        >
          {accion.etiqueta}
        </Link>
      )}
    </div>
  );
}

/** El mensaje lo redacta el backend; acá solo se muestra. */
export function Error({ mensaje, onReintentar }: { mensaje: string; onReintentar?: () => void }) {
  return (
    <div
      role="alert"
      className="rounded-[14px] border border-ambar bg-trigo px-6 py-8 text-center text-marino"
    >
      <p className="text-[15px]">{mensaje}</p>
      {onReintentar && (
        <button
          type="button"
          onClick={onReintentar}
          className="mt-4 h-10 cursor-pointer rounded-[10px] border border-ambar-hondo px-4 text-[13px] font-semibold text-ambar-hondo"
        >
          Volver a intentar
        </button>
      )}
    </div>
  );
}

export function SinPermiso({ detalle }: { detalle?: string }) {
  return (
    <div className="rounded-[14px] border border-arena bg-white px-6 py-12 text-center">
      <p className="font-jakarta text-[18px] font-bold text-marino">Acceso denegado</p>
      <p className="mx-auto mt-2 max-w-[420px] text-[14px] text-pizarra">
        {detalle ?? "Tu cuenta no puede ver esta sección."}
      </p>
    </div>
  );
}

/** Sección que el plan de la tienda no incluye. */
export function BloqueadaPorPlan({ plan, etiqueta }: { plan: Plan; etiqueta: string }) {
  return (
    <div className="rounded-[14px] border border-arena bg-white px-6 py-12 text-center">
      <span className="mx-auto flex size-12 items-center justify-center rounded-full bg-cielo text-acero">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
          <rect x="5" y="11" width="14" height="9" rx="2" />
          <path d="M8 11V8a4 4 0 018 0v3" />
        </svg>
      </span>
      <p className="mt-4 font-jakarta text-[18px] font-bold text-marino">
        Disponible en el plan {NOMBRE_DEL_PLAN[plan]}
      </p>
      <p className="mx-auto mt-2 max-w-[420px] text-[14px] text-pizarra">
        {etiqueta} viene con el plan {NOMBRE_DEL_PLAN[plan]}. Tu tienda está en otro plan.
      </p>
      <Link
        href="/panel/plan"
        className="mt-5 inline-flex h-11 items-center rounded-[12px] bg-acero px-5 text-[14px] font-semibold text-white no-underline hover:bg-acero-hondo hover:no-underline"
      >
        Ver los planes
      </Link>
    </div>
  );
}

/** Sección anunciada pero no construida. */
export function Proximamente({ titulo, detalle }: { titulo: string; detalle: string }) {
  return (
    <div className="rounded-[14px] border border-dashed border-arena-honda bg-white px-6 py-12 text-center">
      <span className="rounded-full bg-hueso px-3 py-1 text-[11px] font-semibold tracking-[0.06em] text-pizarra uppercase">
        Próximamente
      </span>
      <p className="mt-4 font-jakarta text-[18px] font-bold text-marino">{titulo}</p>
      <p className="mx-auto mt-2 max-w-[460px] text-[14px] leading-[1.55] text-pizarra">{detalle}</p>
    </div>
  );
}

/** Lo que falta construir, dicho sin inventar datos. */
export function SinConectar({ seccion }: { seccion: string }) {
  return (
    <div className="rounded-[14px] border border-dashed border-arena-honda bg-white px-6 py-12 text-center">
      <p className="font-jakarta text-[17px] font-bold text-marino">
        Esta función todavía no está conectada
      </p>
      <p className="mx-auto mt-2 max-w-[460px] text-[14px] text-pizarra">
        {seccion} necesita su backend. Prefiere quedarse en blanco antes que mostrarte números
        inventados.
      </p>
    </div>
  );
}
