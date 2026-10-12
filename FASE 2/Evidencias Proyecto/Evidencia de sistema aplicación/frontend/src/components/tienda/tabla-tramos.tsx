import { formatearGramos, formatearPesos } from "@/lib/formato";
import type { TramoGranel } from "@/lib/tipos";
import { cn } from "@/lib/utils";

/*
 * Tramos de una línea de granel.
 *
 * Los umbrales se muestran en la unidad en que los definió la tienda: unos en
 * pesos y otros en gramos. No se convierten entre sí para no mostrar números
 * que la tienda nunca escribió.
 *
 * El tramo activo lo indica el backend en la cotización; acá solo se resalta.
 */
export function TablaDeTramos({ tramos, activo }: { tramos: TramoGranel[]; activo: number | null }) {
  if (tramos.length === 0) {
    return null;
  }

  return (
    <div className="overflow-hidden rounded-[14px] border border-lila/16">
      <div className="flex items-center justify-between bg-superficie px-[18px] py-3.5">
        <span className="text-[13px] font-semibold text-texto">Precio por gramo</span>
        <span className="text-[11px] tracking-[.08em] text-texto-suave uppercase">Neto</span>
      </div>

      {tramos.map((tramo, indice) => {
        const encendido = indice === activo;
        return (
          <div
            key={`${tramo.unidadUmbral}-${tramo.umbral}`}
            className={cn(
              "flex items-center justify-between gap-3.5 border-t border-lila/12 px-[18px] py-[15px] transition-[background-color] duration-200",
              encendido && "bg-violeta/20 shadow-[inset_3px_0_0_#A78BFA]",
            )}
          >
            <span className={cn("text-sm", encendido ? "font-semibold text-texto" : "text-texto-suave")}>
              Desde{" "}
              {tramo.unidadUmbral === "pesos"
                ? formatearPesos(tramo.umbral)
                : formatearGramos(tramo.umbral)}
            </span>
            <span className={cn("font-serif text-[21px] font-semibold", encendido ? "text-oro" : "text-texto-suave")}>
              {formatearPesos(tramo.precioGramoNeto)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
