import Link from "next/link";

import type { Categoria, ContenidoTienda, ProductoResumen } from "@/lib/tipos";

import { IconoCategoria } from "./iconos";
import { TarjetaProducto } from "./tarjeta-producto";

// Degradados de las tarjetas de categoría del mockup, en el mismo orden.
const FONDOS_CATEGORIA = ["#2A2340", "#272042", "#2E2438", "#231F3D"];

/** Categorías destacadas: tarjetas en escritorio, fila de chips en móvil (1A y 1D). */
export function CategoriasDestacadas({
  slugTienda,
  categorias,
}: {
  slugTienda: string;
  categorias: Categoria[];
}) {
  const base = `/t/${slugTienda}`;

  return (
    <>
      <section className="mx-auto hidden w-full max-w-[1440px] px-20 pt-16 lg:block">
        <div className="flex items-baseline justify-between">
          <h2 className="font-serif text-[32px] font-medium text-texto">Categorías destacadas</h2>
          <Link href={`${base}/catalogo`} className="text-[13px] text-lila">
            Ver todo
          </Link>
        </div>

        <div className="mt-6 grid grid-cols-4 gap-5">
          {categorias.map((categoria, indice) => (
            <Link
              key={categoria.slug}
              href={`${base}/catalogo?categoria=${categoria.slug}`}
              style={{
                backgroundImage: `radial-gradient(110% 100% at 20% 15%, ${FONDOS_CATEGORIA[indice % FONDOS_CATEGORIA.length]} 0%, #16141D 70%)`,
              }}
              className="flex h-[170px] flex-col justify-between rounded-2xl border border-lila/12 p-5 transition-colors hover:border-lila/45"
            >
              <IconoCategoria slug={categoria.slug} tamano={40} grosor={1.4} />
              <div className="font-serif text-[23px] text-texto">{categoria.nombre}</div>
            </Link>
          ))}
        </div>
      </section>

      <section className="px-5 pt-[26px] lg:hidden">
        <h2 className="font-serif text-2xl text-texto">Categorías</h2>
        <div className="mt-3.5 flex gap-2.5 overflow-x-auto [scrollbar-width:none]">
          {categorias.map((categoria) => (
            <Link
              key={categoria.slug}
              href={`${base}/catalogo?categoria=${categoria.slug}`}
              className="flex-none rounded-[20px] border border-lila/18 px-4 py-[9px] text-[13px] text-texto-suave"
            >
              {categoria.nombre}
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}

/** "Lo más pedido" (1A y 1D). */
export function MasPedidos({
  slugTienda,
  productos,
}: {
  slugTienda: string;
  productos: ProductoResumen[];
}) {
  return (
    <section className="mx-auto w-full max-w-[1440px] px-5 pt-[26px] lg:px-20 lg:pt-[62px] lg:pb-[76px]">
      <div className="flex items-baseline justify-between">
        <h2 className="font-serif text-2xl text-texto lg:text-[32px] lg:font-medium">Lo más pedido</h2>
        <Link href={`/t/${slugTienda}/catalogo`} className="text-xs text-lila lg:hidden">
          Ver todo
        </Link>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3.5 md:grid-cols-3 lg:mt-[26px] lg:grid-cols-4 lg:gap-[22px]">
        {productos.map((producto) => (
          <TarjetaProducto key={producto.slug} slugTienda={slugTienda} producto={producto} altura="inicio" />
        ))}
      </div>
    </section>
  );
}

/** Llamado a crear cuenta mayorista (1A y 1D). */
export function LlamadoMayorista({ tienda }: { tienda: ContenidoTienda }) {
  const llamado = tienda.llamadoMayorista;

  return (
    <>
      <section className="mx-auto hidden w-full max-w-[1440px] px-20 pb-[76px] lg:block">
        <div className="flex items-center gap-10 rounded-[18px] border border-violeta/35 bg-[linear-gradient(100deg,rgba(124,58,237,.20)_0%,rgba(11,10,15,.2)_70%)] px-12 py-10">
          <h2 className="flex-1 font-serif text-[30px] font-normal text-texto">{llamado.titulo}</h2>
          <button
            type="button"
            aria-disabled="true"
            data-pendiente="cuenta-mayorista"
            className="h-[50px] cursor-pointer rounded-full bg-violeta px-[26px] text-sm font-semibold text-white transition-colors hover:bg-violeta-hover"
          >
            {llamado.boton}
          </button>
        </div>
      </section>

      <section className="px-5 pt-7 pb-[30px] lg:hidden">
        <div className="rounded-2xl border border-violeta/35 bg-[linear-gradient(140deg,rgba(124,58,237,.22),rgba(11,10,15,.2))] p-[22px]">
          <h2 className="font-serif text-[22px] font-normal text-texto">{llamado.titulo}</h2>
          <button
            type="button"
            aria-disabled="true"
            data-pendiente="cuenta-mayorista"
            className="mt-4 h-[46px] w-full cursor-pointer rounded-full border border-lila/45 bg-transparent text-[13px] font-medium text-texto"
          >
            {llamado.movil.boton}
          </button>
        </div>
      </section>
    </>
  );
}
