import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Paginacion } from "@/components/tienda/paginacion";
import { TarjetaLote } from "@/components/tienda/tarjeta-lote";
import { obtenerLotes } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Lotes" };

function numeroDePagina(valor: string | string[] | undefined): number {
  const numero = Number(Array.isArray(valor) ? valor[0] : valor);
  return Number.isInteger(numero) && numero >= 1 ? numero : 1;
}

/** Listado de lotes de la tienda. */
export default async function PaginaLotes({ params, searchParams }: PageProps<"/t/[slug]/lotes">) {
  const { slug } = await params;
  const { pagina } = await searchParams;

  const tienda = await obtenerIdentidadTienda(slug);
  if (!tienda) {
    notFound();
  }

  const catalogo = await obtenerLotes(slug, numeroDePagina(pagina));

  return (
    <main className="mx-auto w-full max-w-[1280px] flex-1 px-5 py-10 lg:px-6">
      <h1 className="font-serif text-[38px] font-medium text-texto lg:text-[44px]">Lotes</h1>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {catalogo.lotes.map((lote) => (
          <TarjetaLote key={lote.codigo} slugTienda={slug} lote={lote} />
        ))}
      </div>

      <div className="mt-10">
        <Paginacion
          base={`/t/${slug}/lotes`}
          paginaActual={catalogo.paginaActual}
          totalPaginas={catalogo.totalPaginas}
        />
      </div>
    </main>
  );
}
