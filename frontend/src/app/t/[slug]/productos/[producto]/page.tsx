import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { FichaProducto } from "@/components/tienda/ficha-producto";
import { obtenerProducto } from "@/lib/api/catalogo";
import { obtenerTienda } from "@/lib/api/tienda";

export async function generateMetadata({ params }: PageProps<"/t/[slug]/productos/[producto]">): Promise<Metadata> {
  const { slug, producto } = await params;
  const detalle = await obtenerProducto(slug, producto);

  return detalle ? { title: detalle.nombre } : {};
}

/** Ficha de producto (mockup 1C). */
export default async function PaginaProducto({ params }: PageProps<"/t/[slug]/productos/[producto]">) {
  const { slug, producto: slugProducto } = await params;
  const [tienda, producto] = await Promise.all([obtenerTienda(slug), obtenerProducto(slug, slugProducto)]);

  if (!tienda || !producto) {
    notFound();
  }

  const base = `/t/${slug}`;

  return (
    <main className="flex-1">
      <nav
        aria-label="Ubicación"
        className="mx-auto max-w-[1280px] px-5 pt-[26px] text-xs text-texto-suave lg:px-6 lg:pt-[34px]"
      >
        <Link href={base} className="transition-colors hover:text-texto">
          Inicio
        </Link>
        {" · "}
        <Link href={`${base}/catalogo?categoria=${producto.categoria.slug}`} className="transition-colors hover:text-texto">
          {producto.categoria.nombre}
        </Link>
        {" · "}
        <span className="text-texto">{producto.nombre}</span>
      </nav>

      <FichaProducto producto={producto} enlaceWhatsapp={tienda.redes.whatsapp} />
    </main>
  );
}
