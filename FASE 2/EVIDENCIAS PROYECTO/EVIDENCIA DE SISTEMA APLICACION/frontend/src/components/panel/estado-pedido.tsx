import type { ReactNode } from "react";

import type { EstadoPedido } from "@/lib/tipos-panel";
import { cn } from "@/lib/utils";

/*
 * La insignia del estado de un pedido.
 *
 * Vive aparte porque la usan el panel (Pedidos, Inicio) y la portada, que
 * muestra un pedido de ejemplo con el mismo aspecto que tendrá adentro. Si los
 * colores cambian, cambian en los dos lados a la vez.
 */

export const ESTILO_DEL_ESTADO: Record<EstadoPedido, string> = {
  PENDIENTE: "border-ambar bg-trigo text-ambar-hondo",
  CONFIRMADO: "border-niebla bg-cielo text-acero",
  ENTREGADO: "border-arena bg-hueso text-pizarra",
  CANCELADO: "border-niebla bg-hueso text-pizarra",
};

/** El nombre que ve el vendedor, igual al que devuelve la API. */
export const NOMBRE_DEL_ESTADO: Record<EstadoPedido, string> = {
  PENDIENTE: "Pendiente de coordinación",
  CONFIRMADO: "Confirmado",
  ENTREGADO: "Entregado",
  CANCELADO: "Cancelado",
};

export function InsigniaDeEstado({
  estado,
  children,
  className,
}: {
  estado: EstadoPedido;
  /** Texto a mostrar; si falta, el nombre estándar del estado. */
  children?: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold whitespace-nowrap",
        ESTILO_DEL_ESTADO[estado],
        className,
      )}
    >
      {children ?? NOMBRE_DEL_ESTADO[estado]}
    </span>
  );
}
