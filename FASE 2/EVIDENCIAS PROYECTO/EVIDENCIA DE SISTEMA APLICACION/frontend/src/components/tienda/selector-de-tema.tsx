"use client";

import { useSyncExternalStore } from "react";

import { CLAVE_DEL_TEMA } from "@/lib/tema";
import type { Tema } from "@/lib/tema";
import { cn } from "@/lib/utils";

import { IconoLuna, IconoSol } from "./iconos";

/*
 * Claro u oscuro, lo elige el comprador.
 *
 * La vitrina nace oscura, que es como está diseñada. Quien prefiera el otro
 * fondo lo cambia acá y su navegador lo recuerda para la próxima; la elección
 * es de quien mira, no de la tienda, así que no viaja al backend ni se comparte
 * entre compradores.
 *
 * Quien manda es el atributo `data-vitrina` del <html>: la hoja de estilos
 * cuelga de ahí el fondo, los textos y cuál de las dos versiones de la paleta
 * de la tienda se usa. El estado de React solo existe para que el botón diga la
 * verdad; si se desincronizara, lo que se ve sigue siendo el atributo.
 */

/*
 * El tema no se guarda en React: se lee del <html>, que es donde el guion lo
 * dejó antes de que React existiera. Acá solo se escucha ese atributo.
 *
 * Suscribirse y no copiar también arregla algo concreto: los encabezados de
 * escritorio y de móvil montan un botón cada uno, y con una copia del estado en
 * cada uno los dos se irían desincronizando.
 */
function suscribir(alCambiar: () => void) {
  const observador = new MutationObserver(alCambiar);
  observador.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-vitrina"],
  });
  return () => observador.disconnect();
}

const leerEnElCliente = (): Tema =>
  document.documentElement.dataset.vitrina === "claro" ? "claro" : "oscuro";

/** En el servidor no hay DOM que leer, y la vitrina nace oscura. */
const leerEnElServidor = (): Tema => "oscuro";

export function SelectorDeTema({ className }: { className?: string }) {
  const tema = useSyncExternalStore(suscribir, leerEnElCliente, leerEnElServidor);

  function alternar() {
    const siguiente: Tema = tema === "claro" ? "oscuro" : "claro";

    document.documentElement.dataset.vitrina = siguiente;

    try {
      localStorage.setItem(CLAVE_DEL_TEMA, siguiente);
    } catch {
      // En ventana privada no se puede guardar. El tema igual queda puesto
      // para esta visita; lo que se pierde es recordarlo en la próxima.
    }
  }

  const aOscuro = tema === "claro";

  return (
    <button
      type="button"
      onClick={alternar}
      aria-label={aOscuro ? "Cambiar a tema oscuro" : "Cambiar a tema claro"}
      title={aOscuro ? "Tema oscuro" : "Tema claro"}
      className={cn(
        "flex size-10 cursor-pointer items-center justify-center rounded-full border border-lila/25 bg-transparent text-texto-suave transition-colors hover:border-lila/50 hover:text-texto",
        className,
      )}
    >
      {aOscuro ? <IconoLuna /> : <IconoSol />}
    </button>
  );
}
