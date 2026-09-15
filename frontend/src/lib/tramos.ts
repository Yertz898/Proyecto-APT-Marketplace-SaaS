import type { TramoPrecio } from "@/lib/tipos";

/**
 * Tramo que corresponde a una cantidad: el de mayor cantidad mínima que la
 * cantidad alcance (CONVENCIONES.md > Tramos de precio).
 *
 * Solo sirve para mostrar el precio mientras el comprador elige la cantidad.
 * El precio que vale es el que calcula el backend al crear el pedido.
 */
export function tramoParaCantidad(
  tramos: TramoPrecio[],
  cantidad: number,
): TramoPrecio | null {
  let aplicable: TramoPrecio | null = null;
  for (const tramo of tramos) {
    if (
      cantidad >= tramo.cantidadMinima &&
      (aplicable === null || tramo.cantidadMinima > aplicable.cantidadMinima)
    ) {
      aplicable = tramo;
    }
  }
  return aplicable;
}

/** "1 – 5 unidades", "6 – 11 unidades", "12 o más unidades" (textos del mockup). */
export function rangoDeTramo(tramos: TramoPrecio[], indice: number): string {
  const ordenados = [...tramos].sort((a, b) => a.cantidadMinima - b.cantidadMinima);
  const tramo = ordenados[indice];
  const siguiente = ordenados[indice + 1];
  if (!siguiente) {
    return `${tramo.cantidadMinima} o más unidades`;
  }
  return `${tramo.cantidadMinima} – ${siguiente.cantidadMinima - 1} unidades`;
}
