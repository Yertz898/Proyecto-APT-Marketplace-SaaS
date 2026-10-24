import type { ReactNode } from "react";

/*
 * Piezas que se repiten en casi todas las secciones de la portada: el
 * encabezado de sección (antetítulo más título) y los dos tipos de franja.
 *
 * Están juntas acá para que los valores de espaciado y tipografía se escriban
 * una vez. Si mañana el antetítulo cambia de tamaño, cambia en las seis
 * secciones a la vez.
 */

/** Franja sobre el fondo hueso de la página. */
export function Franja({
  id,
  className = "",
  children,
}: {
  id?: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className={`px-[clamp(20px,5.5cqi,80px)] ${className}`}>
      <div className="mx-auto flex max-w-[1280px] flex-col gap-[clamp(32px,3.5cqi,48px)]">{children}</div>
    </section>
  );
}

/** Franja blanca, con línea arriba y abajo. Alterna con la anterior. */
export function FranjaClara({
  id,
  children,
}: {
  id?: string;
  children: ReactNode;
}) {
  return (
    <section
      id={id}
      className="border-y border-arena bg-white px-[clamp(20px,5.5cqi,80px)] py-[clamp(64px,7cqi,112px)]"
    >
      <div className="mx-auto flex max-w-[1280px] flex-col gap-[clamp(32px,3.5cqi,48px)]">{children}</div>
    </section>
  );
}

export function TituloDeSeccion({
  antetitulo,
  children,
  bajada,
}: {
  antetitulo: string;
  children: ReactNode;
  bajada?: string;
}) {
  return (
    <div className="flex max-w-[640px] flex-col gap-3">
      <span className="text-[13px] font-semibold tracking-[0.06em] text-acero uppercase">{antetitulo}</span>
      <h2 className="font-jakarta text-[clamp(30px,3.3cqi,46px)] leading-[1.08] font-extrabold tracking-[-0.03em] text-balance">
        {children}
      </h2>
      {bajada && <p className="text-[17px] leading-[1.55] text-pizarra">{bajada}</p>}
    </div>
  );
}
