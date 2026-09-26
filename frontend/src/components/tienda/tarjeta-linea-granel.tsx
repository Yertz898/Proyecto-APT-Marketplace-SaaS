import Link from "next/link";

import { formatearPesos } from "@/lib/formato";
import type { LineaGranel } from "@/lib/tipos";

/**
 * Tarjeta de una línea de granel.
 *
 * Muestra el precio por gramo más bajo de la línea como referencia; el precio
 * que se cobra lo calcula el backend según los gramos que pida el comprador.
 */
export function TarjetaLineaGranel({ slugTienda, linea }: { slugTienda: string; linea: LineaGranel }) {
  const precios = linea.tramos.map((tramo) => tramo.precioGramoNeto);
  const menorPrecio = precios.length > 0 ? Math.min(...precios) : null;

  return (
    <Link
      href={`/t/${slugTienda}/granel/${linea.codigo}`}
      className="flex flex-col rounded-2xl border border-lila/12 bg-superficie p-5 transition-colors hover:border-lila/45"
    >
      <h3 className="font-serif text-[21px] text-texto">{linea.nombre}</h3>
      <p className="mt-1 text-xs text-texto-suave">{linea.material}</p>

      {linea.categorias.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-1.5">
          {linea.categorias.map((categoria) => (
            <li key={categoria} className="rounded-md border border-lila/16 px-2 py-1 text-[11px] text-texto-suave">
              {categoria}
            </li>
          ))}
        </ul>
      )}

      {menorPrecio !== null && (
        <p className="mt-4">
          <span className="text-xs text-texto-suave">desde </span>
          <span className="font-serif text-[21px] font-semibold text-oro">{formatearPesos(menorPrecio)}</span>
          <span className="text-xs text-texto-suave"> por gramo, neto</span>
        </p>
      )}
    </Link>
  );
}
