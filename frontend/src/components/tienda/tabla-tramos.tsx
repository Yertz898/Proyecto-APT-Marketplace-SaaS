import { formatearCantidad, formatearPesos } from "@/lib/formato";
import type { TramoPrecio, UnidadMedida } from "@/lib/tipos";
import { cn } from "@/lib/utils";

/*
 * Los tramos de precio de un producto.
 *
 * Los umbrales se muestran en la unidad en que los definió la tienda —cantidad,
 * monto o peso— y no se convierten entre sí: nadie quiere ver un número que su
 * tienda nunca escribió.
 *
 * El tramo activo lo indica el backend en la cotización; acá solo se resalta.
 */
export function TablaDeTramos({
  tramos,
  unidad,
  activo,
}: {
  tramos: TramoPrecio[];
  unidad: UnidadMedida;
  activo: number | null;
}) {
  if (tramos.length === 0) {
    return null;
  }

  return (
    <div className="overflow-hidden rounded-[14px] border border-lila/16">
      <div className="flex items-center justify-between bg-superficie px-[18px] py-3.5">
        <span className="text-[13px] font-semibold text-texto">{titulo(unidad)}</span>
        <span className="text-[11px] tracking-[.08em] text-texto-suave uppercase">Neto</span>
      </div>

      {tramos.map((tramo) => {
        const encendido = tramo.umbral === activo;
        return (
          <div
            key={`${tramo.unidadUmbral}-${tramo.umbral}`}
            className={cn(
              "flex items-center justify-between gap-3.5 border-t border-lila/12 px-[18px] py-[15px] transition-[background-color] duration-200",
              encendido && "bg-violeta/20 shadow-[inset_3px_0_0_#A78BFA]",
            )}
          >
            <span className={cn("text-sm", encendido ? "font-semibold text-texto" : "text-texto-suave")}>
              Desde {desde(tramo, unidad)}
            </span>
            <span className={cn("font-serif text-[21px] font-semibold", encendido ? "text-oro" : "text-texto-suave")}>
              {formatearPesos(tramo.precioNeto)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/** Cómo se lee el umbral según su unidad. */
function desde(tramo: TramoPrecio, unidad: UnidadMedida): string {
  if (tramo.unidadUmbral === "monto") {
    return formatearPesos(tramo.umbral);
  }
  return formatearCantidad(tramo.umbral, unidad);
}

function titulo(unidad: UnidadMedida): string {
  return unidad === "unidad" ? "Precio por unidad" : `Precio por ${unidad}`;
}
