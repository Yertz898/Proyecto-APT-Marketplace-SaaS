import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { FichaProducto } from "@/components/tienda/ficha-producto";
import { obtenerProducto } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export async function generateMetadata({
  params,
}: PageProps<"/t/[slug]/productos/[codigo]">): Promise<Metadata> {
  const { slug, codigo } = await params;
  const producto = await obtenerProducto(slug, codigo);

  return producto ? { title: producto.nombre } : {};
}

/** Ficha de un producto. */
export default async function PaginaProducto({
  params,
}: PageProps<"/t/[slug]/productos/[codigo]">) {
  const { slug, codigo } = await params;
  const [tienda, producto] = await Promise.all([
    obtenerIdentidadTienda(slug),
    obtenerProducto(slug, codigo),
  ]);

  if (!tienda || !producto) {
    notFound();
  }

  return (
    <main className="mx-auto w-full max-w-[1280px] flex-1 px-5 pt-[26px] pb-12 lg:px-6">
      <nav aria-label="Ubicación" className="text-xs text-texto-suave">
        <Link href={`/t/${slug}/productos`} className="transition-colors hover:text-texto">
          Catálogo
        </Link>
        {" · "}
        <span className="text-texto">{producto.nombre}</span>
      </nav>

      <div className="mt-6">
        <FichaProducto producto={producto} />
      </div>
    </main>
  );
}
