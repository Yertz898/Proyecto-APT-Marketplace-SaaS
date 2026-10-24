import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type Props = {
  enlace: string | null;
  etiqueta?: string;
  className?: string;
  children: ReactNode;
};

/**
 * Enlace a un sitio externo (WhatsApp, Instagram).
 *
 * Si la tienda todavía no tiene el enlace cargado se muestra igual, pero queda
 * inerte. Solo se aceptan direcciones https: hoy el valor lo escribe una persona
 * y mañana lo entregará la API, así que un `javascript:` nunca llega a un href.
 */
export function EnlaceExterno({ enlace, etiqueta, className, children }: Props) {
  if (!enlace || !enlace.startsWith("https://")) {
    return (
      <span
        role="link"
        aria-disabled="true"
        aria-label={etiqueta}
        data-pendiente="enlace-externo"
        className={cn("block", className)}
      >
        {children}
      </span>
    );
  }

  return (
    <a href={enlace} target="_blank" rel="noopener noreferrer" aria-label={etiqueta} className={cn("block", className)}>
      {children}
    </a>
  );
}
