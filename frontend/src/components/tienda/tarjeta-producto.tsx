import Image from "next/image";
import Link from "next/link";

import { formatearPesos } from "@/lib/formato";
import type { ProductoResumen } from "@/lib/tipos";
import { cn } from "@/lib/utils";

type Props = {
  slugTienda: string;
  producto: ProductoResumen;
  altura: "inicio" | "catalogo";
};

/*
 * Tarjeta de producto (mockup 1A, 1B y 1D).
 *
 * "Agregar" no suma al carrito: abre la ficha. Sin elegir material y talla no
 * hay variante, y el stock vive en la variante (CONVENCIONES.md > Modelo de dominio).
 *
 * En pantallas táctiles no existe el hover, así que el botón queda siempre
 * visible en vez de aparecer al pasar el mouse.
 */
export function TarjetaProducto({ slugTienda, producto, altura }: Props) {
  const ficha = `/t/${slugTienda}/productos/${producto.slug}`;
  const minimo = producto.cantidadMinimaMayorista;

  return (
    <article className="group/tarjeta overflow-hidden rounded-[14px] border border-lila/10 bg-superficie transition-[translate,box-shadow,border-color] duration-250 ease-joya hover:-translate-y-2 hover:border-lila/55 hover:shadow-[0_22px_46px_-14px_rgba(124,58,237,.42),0_10px_26px_rgba(0,0,0,.55)] motion-reduce:duration-1 motion-reduce:hover:translate-y-0 lg:rounded-2xl">
      <div
        className={cn(
          "relative h-40 overflow-hidden bg-[radial-gradient(120%_110%_at_28%_18%,#2C2440_0%,#16141D_72%)]",
          altura === "inicio" ? "lg:h-[250px]" : "lg:h-[270px]",
        )}
      >
        {producto.imagen && (
          <Image
            src={producto.imagen.url}
            alt={producto.imagen.alt}
            fill
            sizes="(min-width: 1024px) 25vw, 50vw"
            className="object-cover transition-[scale] duration-250 ease-joya group-hover/tarjeta:scale-106 motion-reduce:group-hover/tarjeta:scale-100"
          />
        )}

        {minimo !== null && (
          <span className="absolute top-2 left-2 rounded-[20px] border border-oro/50 bg-tinta/75 px-[7px] py-1 text-[9px] font-semibold tracking-[.06em] text-oro lg:top-3 lg:left-3 lg:bg-tinta/72 lg:px-[9px] lg:py-[5px] lg:text-[10px] lg:tracking-[.08em]">
            <span className="lg:hidden">DESDE {minimo} UN.</span>
            <span className="hidden lg:inline">DESDE {minimo} UNIDADES</span>
          </span>
        )}

        <Link
          href={ficha}
          aria-label={`Agregar ${producto.nombre}`}
          className="absolute right-2 bottom-2 left-2 flex h-11 translate-y-2 items-center justify-center rounded-[10px] bg-violeta text-[13px] font-semibold text-white opacity-0 transition-[opacity,translate,background-color] duration-250 ease-joya group-hover/tarjeta:translate-y-0 group-hover/tarjeta:opacity-100 hover:bg-violeta-hover focus-visible:translate-y-0 focus-visible:opacity-100 motion-reduce:translate-y-0 motion-reduce:opacity-45 motion-reduce:group-hover/tarjeta:opacity-100 [@media(hover:none)]:translate-y-0 [@media(hover:none)]:opacity-100 lg:right-3 lg:bottom-3 lg:left-3 lg:h-10 lg:rounded-[11px]"
        >
          Agregar
        </Link>
      </div>

      <div className="p-3 lg:px-4 lg:pt-[15px] lg:pb-[17px]">
        <h3 className="font-serif text-[17px] leading-[1.2] text-texto lg:text-[21px]">{producto.nombre}</h3>
        <p className="mt-1 hidden text-xs text-texto-suave lg:block">{producto.resumen}</p>
        <p className="mt-2 flex items-baseline gap-[7px] lg:mt-[11px]">
          <span className="font-serif text-[19px] font-semibold text-oro lg:text-[23px]">
            {formatearPesos(producto.precioDetalle)}
          </span>
          <span className="hidden text-[11px] text-texto-suave lg:inline">c/u</span>
        </p>
      </div>
    </article>
  );
}
