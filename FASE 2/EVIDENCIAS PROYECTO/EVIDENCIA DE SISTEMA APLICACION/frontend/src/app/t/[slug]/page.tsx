import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { obtenerIdentidadTienda } from "@/lib/api/tienda";

/**
 * Inicio de la tienda pública.
 *
 * Lleva al catálogo y nada más: cómo vende esa tienda lo dicen sus productos,
 * no esta pantalla. El banner se muestra solo si la tienda lo cargó: sin imagen
 * no se dibuja nada en su lugar.
 */
export default async function InicioTienda({ params }: PageProps<"/t/[slug]">) {
  const { slug } = await params;
  const tienda = await obtenerIdentidadTienda(slug);

  if (!tienda) {
    notFound();
  }

  const base = `/t/${slug}`;

  return (
    <main className="flex-1">
      {tienda.banner && (
        <div className="relative h-[240px] w-full lg:h-[420px]">
          <Image
            src={tienda.banner.url}
            alt={tienda.banner.alt}
            fill
            sizes="100vw"
            className="object-cover"
            priority
          />
        </div>
      )}

      <div className="mx-auto w-full max-w-[1280px] px-5 py-12 lg:px-6 lg:py-16">
        <h1 className="font-serif text-[38px] font-medium text-texto lg:text-[52px]">{tienda.nombre}</h1>

        <div className="mt-8">
          <Link
            href={`${base}/productos`}
            className="inline-flex h-12 items-center rounded-full bg-violeta px-7 text-sm font-semibold text-white transition-colors hover:bg-violeta-hover hover:no-underline"
          >
            Ver el catálogo
          </Link>
        </div>
      </div>
    </main>
  );
}
