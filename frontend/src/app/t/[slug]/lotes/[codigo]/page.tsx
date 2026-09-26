import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { FichaLote } from "@/components/tienda/ficha-lote";
import { obtenerLote } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export async function generateMetadata({ params }: PageProps<"/t/[slug]/lotes/[codigo]">): Promise<Metadata> {
  const { slug, codigo } = await params;
  const lote = await obtenerLote(slug, codigo);

  return lote ? { title: lote.nombre } : {};
}

/** Ficha de un lote. */
export default async function PaginaLote({ params }: PageProps<"/t/[slug]/lotes/[codigo]">) {
  const { slug, codigo } = await params;
  const [tienda, lote] = await Promise.all([obtenerIdentidadTienda(slug), obtenerLote(slug, codigo)]);

  if (!tienda || !lote) {
    notFound();
  }

  return (
    <main className="flex-1">
      <nav
        aria-label="Ubicación"
        className="mx-auto max-w-[1280px] px-5 pt-[26px] text-xs text-texto-suave lg:px-6"
      >
        <Link href={`/t/${slug}/lotes`} className="transition-colors hover:text-texto">
          Lotes
        </Link>
        {" · "}
        <span className="text-texto">{lote.nombre}</span>
      </nav>

      <FichaLote lote={lote} />
    </main>
  );
}
