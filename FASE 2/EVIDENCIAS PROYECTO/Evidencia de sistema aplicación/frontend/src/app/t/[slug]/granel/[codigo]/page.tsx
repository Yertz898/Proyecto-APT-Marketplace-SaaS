import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { CompraGranel } from "@/components/tienda/compra-granel";
import { obtenerLineaGranel } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export async function generateMetadata({ params }: PageProps<"/t/[slug]/granel/[codigo]">): Promise<Metadata> {
  const { slug, codigo } = await params;
  const linea = await obtenerLineaGranel(slug, codigo);

  return linea ? { title: linea.nombre } : {};
}

/** Compra por gramos de una línea de granel. */
export default async function PaginaLineaGranel({ params }: PageProps<"/t/[slug]/granel/[codigo]">) {
  const { slug, codigo } = await params;
  const [tienda, linea] = await Promise.all([obtenerIdentidadTienda(slug), obtenerLineaGranel(slug, codigo)]);

  if (!tienda || !linea) {
    notFound();
  }

  return (
    <main className="mx-auto w-full max-w-[860px] flex-1 px-5 py-10 lg:px-6">
      <nav aria-label="Ubicación" className="text-xs text-texto-suave">
        <Link href={`/t/${slug}/granel`} className="transition-colors hover:text-texto">
          Granel
        </Link>
        {" · "}
        <span className="text-texto">{linea.nombre}</span>
      </nav>

      <h1 className="mt-3 font-serif text-[36px] leading-[1.1] font-medium text-texto lg:text-[42px]">
        {linea.nombre}
      </h1>
      <p className="mt-2 text-[13px] text-texto-suave">{linea.material}</p>

      <div className="mt-8">
        <CompraGranel slugTienda={slug} linea={linea} />
      </div>
    </main>
  );
}
