"use client";

import { useRef, type ReactNode } from "react";

/*
 * Una fila de tarjetas que se desliza.
 *
 * Es scroll nativo con «snap», no una librería: en el teléfono se arrastra con
 * el dedo como cualquier lista, y en el computador las flechas mueven una
 * pantalla. Sin JavaScript sigue funcionando como una fila que se desplaza.
 */
export function Carrusel({ titulo, children, accion }: { titulo: string; children: ReactNode; accion?: ReactNode }) {
  const pista = useRef<HTMLDivElement>(null);

  function mover(sentido: 1 | -1) {
    const elemento = pista.current;
    if (!elemento) return;
    elemento.scrollBy({ left: sentido * elemento.clientWidth * 0.85, behavior: "smooth" });
  }

  return (
    <section aria-label={titulo} className="mx-auto w-full max-w-[1280px] px-5 lg:px-6">
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2 className="font-serif text-[28px] leading-[1.1] text-texto lg:text-[34px]">{titulo}</h2>
        <div className="flex items-center gap-2">
          {accion}
          <BotonFlecha etiqueta="Anteriores" onClick={() => mover(-1)}>
            ‹
          </BotonFlecha>
          <BotonFlecha etiqueta="Siguientes" onClick={() => mover(1)}>
            ›
          </BotonFlecha>
        </div>
      </div>
      <div
        ref={pista}
        className="-mx-5 flex snap-x snap-mandatory gap-4 overflow-x-auto scroll-smooth px-5 pb-3 [scrollbar-width:thin] lg:-mx-6 lg:px-6"
      >
        {children}
      </div>
    </section>
  );
}

/** Cada tarjeta del carrusel ocupa un ancho fijo para que asomen las siguientes. */
export function Diapositiva({ children }: { children: ReactNode }) {
  return <div className="w-[72%] shrink-0 snap-start sm:w-[44%] lg:w-[23%]">{children}</div>;
}

function BotonFlecha({ etiqueta, onClick, children }: { etiqueta: string; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      aria-label={etiqueta}
      onClick={onClick}
      className="hidden size-10 cursor-pointer items-center justify-center rounded-full border border-lila/25 text-[22px] leading-none text-texto transition-colors hover:bg-violeta/15 sm:flex"
    >
      {children}
    </button>
  );
}
