"use client";

import { useSyncExternalStore } from "react";

import { instantanea, suscribir, type Sesion } from "@/lib/sesion";
import type { Rol } from "@/lib/tipos";

/*
 * La sesión no necesita un proveedor: vive en un único almacén del módulo y
 * cualquier componente la lee de ahí. Un contexto solo agregaría un envoltorio
 * en el layout raíz sin cambiar nada.
 */

const sinCambios = () => () => {};

export type EstadoDeSesion = {
  sesion: Sesion | null;
  /**
   * Si el navegador ya pudo leer el almacenamiento.
   *
   * En el servidor y en el primer dibujo todavía no, y ahí "sin sesión" no
   * quiere decir que no haya: quiere decir que no se sabe. Un guardia que no
   * distinga las dos cosas echa a quien sí tenía sesión.
   */
  hidratado: boolean;
};

export function useSesion(): EstadoDeSesion {
  const sesion = useSyncExternalStore(suscribir, instantanea, () => null);
  const hidratado = useSyncExternalStore(
    sinCambios,
    () => true,
    () => false,
  );

  return { sesion, hidratado };
}

/** Roles que trabajan dentro de una tienda (CLAUDE.md > Roles). */
const ROLES_DE_TIENDA: Rol[] = ["dueno_tienda", "vendedor"];

export function trabajaEnTienda(sesion: Sesion | null): boolean {
  return Boolean(sesion && ROLES_DE_TIENDA.includes(sesion.usuario.rol) && sesion.usuario.tienda);
}
