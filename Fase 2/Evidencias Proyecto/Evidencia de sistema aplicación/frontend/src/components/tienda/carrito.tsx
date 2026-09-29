"use client";

import Link from "next/link";
import { createContext, useCallback, useContext, useSyncExternalStore, type ReactNode } from "react";

import type { LineaCarrito } from "@/lib/tipos";
import { cn } from "@/lib/utils";

import { IconoBolsa } from "./iconos";

/*
 * Carrito del comprador.
 *
 * Guarda solo referencias y cantidades, nunca precios: los tramos de lotes
 * dependen del pedido completo y un cupo puede agotarse mientras el comprador
 * decide, así que cotizar es siempre trabajo del backend.
 *
 * Vive en el almacenamiento del navegador para sobrevivir a una recarga. Es
 * temporal: el carrito de verdad es un pedido en estado `borrador` del backend
 * (CLAUDE.md > Estados del pedido), y lo reemplaza cuando exista la API.
 *
 * Se usa useSyncExternalStore porque el almacenamiento del navegador es
 * justamente eso, un sistema externo: así el servidor entrega un carrito vacío,
 * el navegador lo completa sin desajustar la hidratación, y no hace falta
 * escribir estado dentro de un efecto.
 */

const VACIO: LineaCarrito[] = [];

const escuchas = new Set<() => void>();
let cache: { slug: string; lineas: LineaCarrito[] } | null = null;

function claveDeGuardado(slug: string): string {
  return `dealcommerce:carrito:${slug}`;
}

function leerDelNavegador(slug: string): LineaCarrito[] {
  try {
    const guardado = window.localStorage.getItem(claveDeGuardado(slug));
    const datos: unknown = guardado ? JSON.parse(guardado) : null;
    return Array.isArray(datos) ? (datos as LineaCarrito[]) : VACIO;
  } catch {
    // Navegación privada o almacenamiento bloqueado: se parte con el carrito vacío.
    return VACIO;
  }
}

/** Devuelve siempre la misma referencia mientras el carrito no cambie. */
function instantanea(slug: string): LineaCarrito[] {
  if (!cache || cache.slug !== slug) {
    cache = { slug, lineas: leerDelNavegador(slug) };
  }
  return cache.lineas;
}

function guardar(slug: string, lineas: LineaCarrito[]) {
  cache = { slug, lineas };
  try {
    window.localStorage.setItem(claveDeGuardado(slug), JSON.stringify(lineas));
  } catch {
    // Sin almacenamiento el carrito vive solo mientras dure la pestaña.
  }
  for (const escucha of escuchas) {
    escucha();
  }
}

function suscribir(escucha: () => void): () => void {
  escuchas.add(escucha);
  return () => {
    escuchas.delete(escucha);
  };
}

type Carrito = {
  slugTienda: string;
  lineas: LineaCarrito[];
  agregarLote: (codigo: string, cantidad?: number) => void;
  agregarGranel: (codigo: string, gramos: number) => void;
  quitar: (indice: number) => void;
  vaciar: () => void;
};

const ContextoCarrito = createContext<Carrito | null>(null);

export function ProveedorCarrito({ slugTienda, children }: { slugTienda: string; children: ReactNode }) {
  const lineas = useSyncExternalStore(
    suscribir,
    () => instantanea(slugTienda),
    () => VACIO,
  );

  const agregarLote = useCallback(
    (codigo: string, cantidad = 1) => {
      const actuales = instantanea(slugTienda);
      const posicion = actuales.findIndex((linea) => linea.tipo === "lote" && linea.codigo === codigo);

      if (posicion === -1) {
        guardar(slugTienda, [...actuales, { tipo: "lote", codigo, cantidad }]);
        return;
      }

      guardar(
        slugTienda,
        actuales.map((linea, indice) =>
          indice === posicion && linea.tipo === "lote" ? { ...linea, cantidad: linea.cantidad + cantidad } : linea,
        ),
      );
    },
    [slugTienda],
  );

  const agregarGranel = useCallback(
    (codigo: string, gramos: number) => {
      const actuales = instantanea(slugTienda);
      const posicion = actuales.findIndex((linea) => linea.tipo === "granel" && linea.codigo === codigo);

      if (posicion === -1) {
        guardar(slugTienda, [...actuales, { tipo: "granel", codigo, gramos }]);
        return;
      }

      guardar(
        slugTienda,
        actuales.map((linea, indice) =>
          indice === posicion && linea.tipo === "granel" ? { ...linea, gramos: linea.gramos + gramos } : linea,
        ),
      );
    },
    [slugTienda],
  );

  const quitar = useCallback(
    (indice: number) => {
      guardar(
        slugTienda,
        instantanea(slugTienda).filter((_, posicion) => posicion !== indice),
      );
    },
    [slugTienda],
  );

  const vaciar = useCallback(() => guardar(slugTienda, []), [slugTienda]);

  return (
    <ContextoCarrito value={{ slugTienda, lineas, agregarLote, agregarGranel, quitar, vaciar }}>
      {children}
    </ContextoCarrito>
  );
}

export function useCarrito(): Carrito {
  const carrito = useContext(ContextoCarrito);
  if (!carrito) {
    throw new Error("useCarrito debe usarse dentro de <ProveedorCarrito>.");
  }
  return carrito;
}

/** Ícono del carrito con la cantidad de líneas. */
export function ContadorCarrito({ variante }: { variante: "escritorio" | "movil" }) {
  const { lineas, slugTienda } = useCarrito();
  const movil = variante === "movil";

  return (
    <Link
      href={`/t/${slugTienda}/carrito`}
      aria-label={`Carrito: ${lineas.length} ${lineas.length === 1 ? "línea" : "líneas"}`}
      className="relative block"
    >
      <IconoBolsa tamano={movil ? 20 : 21} />
      <span
        className={cn(
          "absolute flex items-center justify-center bg-violeta px-1 text-[10px] font-semibold text-white",
          movil ? "-top-1.5 -right-[7px] h-4 min-w-4 rounded-lg" : "-top-1.5 -right-2 h-[17px] min-w-[17px] rounded-[9px]",
        )}
      >
        {lineas.length}
      </span>
    </Link>
  );
}
