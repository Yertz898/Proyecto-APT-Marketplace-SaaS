import type { UsuarioSesion } from "@/lib/tipos";

/*
 * Sesión del navegador.
 *
 * Guarda los dos tokens y quién inició sesión, para que una recarga no obligue
 * a entrar de nuevo. Se lee con useSyncExternalStore por lo mismo que el
 * carrito: el almacenamiento del navegador es un sistema externo, así el
 * servidor entrega "sin sesión", el navegador la completa sin desajustar la
 * hidratación y no hace falta escribir estado dentro de un efecto.
 *
 * PENDIENTE DE SEGURIDAD: los tokens quedan en localStorage, así que un script
 * inyectado en la página podría leerlos. Lo que de verdad los protege es una
 * cookie httpOnly, y eso significa que el navegador deje de hablarle directo a
 * Django y pase por el servidor de Next. Es una decisión de arquitectura que no
 * está tomada; mientras no se tome, la defensa es no renderizar nunca HTML ni
 * CSS escrito por un vendedor (ver ColoresTienda en tipos.ts).
 */

export type Sesion = {
  acceso: string;
  refresco: string;
  usuario: UsuarioSesion;
};

const CLAVE = "dealcommerce:sesion";

const escuchas = new Set<() => void>();

//: `undefined` es "todavía no se leyó"; `null` es "no hay sesión".
let cache: Sesion | null | undefined;

function leerDelNavegador(): Sesion | null {
  try {
    const guardado = window.localStorage.getItem(CLAVE);
    if (!guardado) {
      return null;
    }

    const datos = JSON.parse(guardado) as Partial<Sesion>;
    // Un formato viejo o a medias se descarta: es preferible pedir la sesión
    // de nuevo antes que trabajar con un usuario incompleto.
    return datos.acceso && datos.refresco && datos.usuario ? (datos as Sesion) : null;
  } catch {
    return null;
  }
}

function avisar() {
  for (const escucha of escuchas) {
    escucha();
  }
}

/** Devuelve siempre la misma referencia mientras la sesión no cambie. */
export function instantanea(): Sesion | null {
  if (cache === undefined) {
    cache = leerDelNavegador();
  }
  return cache;
}

export function suscribir(escucha: () => void): () => void {
  escuchas.add(escucha);
  return () => {
    escuchas.delete(escucha);
  };
}

export function guardarSesion(sesion: Sesion) {
  cache = sesion;
  try {
    window.localStorage.setItem(CLAVE, JSON.stringify(sesion));
  } catch {
    // Sin almacenamiento la sesión dura lo que dure la pestaña.
  }
  avisar();
}

export function borrarSesion() {
  cache = null;
  try {
    window.localStorage.removeItem(CLAVE);
  } catch {
    // Nada que limpiar.
  }
  avisar();
}

/** Reemplaza solo el token de acceso, después de renovarlo. */
export function guardarAcceso(acceso: string) {
  const actual = instantanea();
  if (actual) {
    guardarSesion({ ...actual, acceso });
  }
}

export function tokenDeAcceso(): string | null {
  return instantanea()?.acceso ?? null;
}
