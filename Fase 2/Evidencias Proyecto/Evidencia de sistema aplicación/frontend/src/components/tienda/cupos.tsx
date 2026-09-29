import type { Cupos } from "@/lib/tipos";

/**
 * Estado de cupos de un lote.
 *
 * UNICO no se repite y lleva su insignia; MULTIPLE muestra cuántos quedan.
 */
export function InsigniaCupos({ cupos, agotado }: { cupos: Cupos; agotado: boolean }) {
  if (agotado) {
    return (
      <span className="flex-none rounded-[20px] border border-texto-suave/40 px-[9px] py-1 text-[10px] font-semibold tracking-[.08em] text-texto-suave uppercase">
        Agotado
      </span>
    );
  }

  if (cupos.tipo === "UNICO") {
    return (
      <span className="flex-none rounded-[20px] border border-oro/50 px-[9px] py-1 text-[10px] font-semibold tracking-[.08em] text-oro uppercase">
        Cupo único
      </span>
    );
  }

  return (
    <span className="flex-none rounded-[20px] border border-lila/28 px-[9px] py-1 text-[10px] font-semibold tracking-[.08em] text-lila uppercase">
      {cupos.restantes} {cupos.restantes === 1 ? "cupo" : "cupos"}
    </span>
  );
}
