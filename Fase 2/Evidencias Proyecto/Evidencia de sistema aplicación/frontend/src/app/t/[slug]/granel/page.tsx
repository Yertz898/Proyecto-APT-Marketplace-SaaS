import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { TarjetaLineaGranel } from "@/components/tienda/tarjeta-linea-granel";
import { obtenerLineasGranel } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Granel" };

/** Listado de líneas de granel de la tienda. */
export default async function PaginaGranel({ params }: PageProps<"/t/[slug]/granel">) {
  const { slug } = await params;

  const tienda = await obtenerIdentidadTienda(slug);
  if (!tienda) {
    notFound();
  }

  const lineas = await obtenerLineasGranel(slug);

  return (
    <main className="mx-auto w-full max-w-[1280px] flex-1 px-5 py-10 lg:px-6">
      <h1 className="font-serif text-[38px] font-medium text-texto lg:text-[44px]">Granel</h1>
      <p className="mt-2 text-sm text-texto-suave">Compra por gramo. El precio depende de la cantidad.</p>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {lineas.map((linea) => (
          <TarjetaLineaGranel key={linea.codigo} slugTienda={slug} linea={linea} />
        ))}
      </div>
    </main>
  );
}
