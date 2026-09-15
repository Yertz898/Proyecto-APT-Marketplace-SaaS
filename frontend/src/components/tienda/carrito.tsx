"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

import { cn } from "@/lib/utils";

import { IconoBolsa } from "./iconos";

/*
 * Contador del carrito en memoria, igual que en el mockup.
 *
 * No persiste ni crea pedidos: se pierde al recargar la página. El carrito real
 * es un pedido en estado `borrador` del backend (CONVENCIONES.md > Estados del pedido)
 * y reemplaza a este contexto cuando exista la API.
 */

type Carrito = {
  unidades: number;
  agregar: (cantidad: number) => void;
};

const ContextoCarrito = createContext<Carrito | null>(null);

export function ProveedorCarrito({ children }: { children: ReactNode }) {
  const [unidades, setUnidades] = useState(0);
  const agregar = (cantidad: number) => setUnidades((actual) => actual + cantidad);

  return <ContextoCarrito value={{ unidades, agregar }}>{children}</ContextoCarrito>;
}

export function useCarrito(): Carrito {
  const carrito = useContext(ContextoCarrito);
  if (!carrito) {
    throw new Error("useCarrito debe usarse dentro de <ProveedorCarrito>.");
  }
  return carrito;
}

/** Ícono del carrito con su contador. La pantalla del carrito no está diseñada: queda inerte. */
export function ContadorCarrito({ variante }: { variante: "escritorio" | "movil" }) {
  const { unidades } = useCarrito();
  const movil = variante === "movil";

  return (
    <button
      type="button"
      aria-disabled="true"
      data-pendiente="carrito"
      aria-label={`Carrito: ${unidades} unidades`}
      className="relative block cursor-pointer"
    >
      <IconoBolsa tamano={movil ? 20 : 21} />
      <span
        className={cn(
          "absolute flex items-center justify-center bg-violeta px-1 text-[10px] font-semibold text-white",
          movil ? "-top-1.5 -right-[7px] h-4 min-w-4 rounded-lg" : "-top-1.5 -right-2 h-[17px] min-w-[17px] rounded-[9px]",
        )}
      >
        {unidades}
      </span>
    </button>
  );
}
