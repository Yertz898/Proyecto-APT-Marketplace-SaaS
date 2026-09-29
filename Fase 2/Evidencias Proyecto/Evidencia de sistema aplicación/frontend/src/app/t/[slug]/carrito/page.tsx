import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { VistaCarrito } from "@/components/tienda/vista-carrito";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Carrito" };

/** Carrito y checkout simulado de la tienda. */
export default async function PaginaCarrito({ params }: PageProps<"/t/[slug]/carrito">) {
  const { slug } = await params;
  const tienda = await obtenerIdentidadTienda(slug);

  if (!tienda) {
    notFound();
  }

  return (
    <main className="mx-auto w-full max-w-[1100px] flex-1 px-5 py-10 lg:px-6">
      <h1 className="font-serif text-[38px] font-medium text-texto">Carrito</h1>
      <div className="mt-8">
        <VistaCarrito slugTienda={slug} />
      </div>
    </main>
  );
}
