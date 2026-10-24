import type { Disponibilidad } from "@/lib/tipos";

/**
 * Lo que se le puede decir al comprador sobre las existencias.
 *
 * Quién decide es el backend: acá solo se dibuja. Una tienda que no lleva
 * inventario no muestra insignia, porque no sabe cuánto le queda e inventar un
 * número sería mentir.
 */
export function InsigniaDisponibilidad({ disponibilidad }: { disponibilidad: Disponibilidad }) {
  if (disponibilidad.tipo === "sin_control") {
    return null;
  }

  if (disponibilidad.tipo === "agotado") {
    return (
      <span className="flex-none rounded-[20px] border border-texto-suave/40 px-[9px] py-1 text-[10px] font-semibold tracking-[.08em] text-texto-suave uppercase">
        Agotado
      </span>
    );
  }

  if (disponibilidad.tipo === "ultima") {
    return (
      <span className="flex-none rounded-[20px] border border-oro/50 px-[9px] py-1 text-[10px] font-semibold tracking-[.08em] text-oro uppercase">
        Queda uno
      </span>
    );
  }

  return (
    <span className="flex-none rounded-[20px] border border-lila/28 px-[9px] py-1 text-[10px] font-semibold tracking-[.08em] text-lila uppercase">
      Quedan {disponibilidad.restantes}
    </span>
  );
}
