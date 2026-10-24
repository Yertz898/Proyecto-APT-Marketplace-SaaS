import Image from "next/image";
import Link from "next/link";

import { formatearCantidad, formatearPesos } from "@/lib/formato";
import type { Producto } from "@/lib/tipos";

import { InsigniaDisponibilidad } from "./disponibilidad";

/*
 * Un producto en la grilla del catálogo.
 *
 * Es una sola tarjeta para las tres formas de venta. Lo que cambia no es el
 * componente sino los datos: un producto por lote trae su composición, uno por
 * peso trae tramos, y lo que no aplica simplemente no se dibuja.
 */
export function TarjetaProducto({
  slugTienda,
  producto,
}: {
  slugTienda: string;
  producto: Producto;
}) {
  const desde = precioDesde(producto);

  return (
    <Link
      href={`/t/${slugTienda}/productos/${encodeURIComponent(producto.codigo)}`}
      className="group flex flex-col overflow-hidden rounded-[18px] border border-lila/12 bg-superficie transition-colors hover:border-lila/45 hover:no-underline"
    >
      {producto.foto && (
        <Image
          src={producto.foto.url}
          alt={producto.foto.alt}
          width={420}
          height={280}
          className="h-[180px] w-full object-cover"
        />
      )}

      <div className="flex flex-1 flex-col p-5">
        <span className="flex items-start justify-between gap-3">
          <span className="font-serif text-[19px] leading-[1.25] text-texto">{producto.nombre}</span>
          <InsigniaDisponibilidad disponibilidad={producto.disponibilidad} />
        </span>

        {producto.descripcion && (
          <span className="mt-1.5 text-[13px] leading-[1.5] text-texto-suave">
            {producto.descripcion}
          </span>
        )}

        {producto.piezasTotales !== null && (
          <span className="mt-1.5 text-[13px] text-texto-suave">
            {producto.piezasTotales} piezas
          </span>
        )}

        {producto.composicion.length > 0 && (
          <span className="mt-3 flex flex-wrap gap-1.5">
            {producto.composicion.map((parte) => (
              <span
                key={parte.categoria}
                className="rounded-md border border-lila/16 px-2 py-1 text-[11px] text-texto-suave"
              >
                {parte.cantidad} {parte.categoria}
              </span>
            ))}
          </span>
        )}

        <span className="mt-4 flex-1" />

        <span className="font-serif text-[22px] font-semibold text-oro">
          {desde.prefijo}
          {formatearPesos(desde.monto)}
        </span>
        <span className="text-[12px] text-texto-suave">{desde.detalle}</span>
      </div>
    </Link>
  );
}

/**
 * Qué precio se muestra en la tarjeta.
 *
 * Con tramos, el más barato con un "desde": es lo que el comprador quiere
 * comparar de un vistazo. Sin tramos, el precio a secas.
 */
function precioDesde(producto: Producto): {
  prefijo: string;
  monto: number;
  detalle: string;
} {
  const porUnidad =
    producto.unidadMedida === "unidad"
      ? "neto"
      : `por ${producto.unidadMedida}, neto`;

  if (producto.tramos.length === 0) {
    return { prefijo: "", monto: producto.precioNeto, detalle: porUnidad };
  }

  const barato = Math.min(...producto.tramos.map((tramo) => tramo.precioNeto));
  return { prefijo: "desde ", monto: barato, detalle: porUnidad };
}

/** El mínimo de compra, cuando la tienda lo definió. */
export function MinimoDeCompra({ producto }: { producto: Producto }) {
  if (producto.minimo) {
    return <span className="text-[12px] text-texto-suave">{producto.minimo}</span>;
  }

  if (producto.cantidadMinima > 1) {
    return (
      <span className="text-[12px] text-texto-suave">
        Mínimo {formatearCantidad(producto.cantidadMinima, producto.unidadMedida)}
      </span>
    );
  }

  return null;
}
