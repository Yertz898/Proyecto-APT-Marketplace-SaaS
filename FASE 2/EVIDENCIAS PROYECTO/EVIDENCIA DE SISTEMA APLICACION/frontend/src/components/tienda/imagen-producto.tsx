import { Gem, Package, Scale } from "lucide-react";
import Image from "next/image";

import type { FormaVenta, Producto } from "@/lib/tipos";
import { cn } from "@/lib/utils";

/*
 * La imagen de un producto, o su símbolo cuando todavía no tiene foto.
 *
 * Un producto que se vende por gramo casi nunca tiene una foto que lo
 * represente: se dibuja una balanza. Un lote sin foto lleva una caja y una
 * pieza suelta una gema. Así la grilla no queda con huecos y el comprador ve
 * de un vistazo cómo se vende cada cosa.
 */

const ETIQUETA: Record<FormaVenta, string> = {
  peso: "Por peso",
  lote: "Por lote",
  unidad: "Por unidad",
};

function Simbolo({ forma, tamano }: { forma: FormaVenta; tamano: number }) {
  const props = { size: tamano, strokeWidth: 1.6, "aria-hidden": true } as const;
  if (forma === "peso") return <Scale {...props} />;
  if (forma === "lote") return <Package {...props} />;
  return <Gem {...props} />;
}

export function ImagenDeProducto({
  producto,
  alto,
  grande = false,
  sizes = "(min-width: 1024px) 25vw, 50vw",
}: {
  producto: Producto;
  /** Clase de alto del recuadro, p. ej. "h-[190px]". */
  alto: string;
  /** En la ficha el símbolo va más grande. */
  grande?: boolean;
  sizes?: string;
}) {
  return (
    <div className={cn("relative w-full overflow-hidden", alto)}>
      {producto.foto ? (
        <Image src={producto.foto.url} alt={producto.foto.alt} fill sizes={sizes} className="object-cover" />
      ) : (
        <div
          role="img"
          aria-label={`${producto.nombre}, ${ETIQUETA[producto.formaVenta].toLowerCase()}`}
          className="flex h-full w-full items-center justify-center bg-gradient-to-br from-violeta/30 via-tinta to-tinta-honda"
        >
          <span
            className={cn(
              "flex items-center justify-center rounded-full border border-oro/45 bg-oro/10 text-oro",
              grande ? "size-28" : "size-16",
            )}
          >
            <Simbolo forma={producto.formaVenta} tamano={grande ? 48 : 28} />
          </span>
        </div>
      )}
      <span className="absolute top-3 left-3 rounded-full bg-tinta/80 px-2.5 py-1 text-[11px] font-semibold text-texto backdrop-blur-sm">
        {ETIQUETA[producto.formaVenta]}
      </span>
    </div>
  );
}
