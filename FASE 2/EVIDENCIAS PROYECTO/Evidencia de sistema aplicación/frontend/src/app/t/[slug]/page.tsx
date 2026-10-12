import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { obtenerIdentidadTienda } from "@/lib/api/tienda";

/**
 * Inicio de la tienda pública.
 *
 * Las dos formas de comprar de la plataforma son lotes y granel. El banner se
 * muestra solo si la tienda lo cargó: sin imagen no se dibuja nada en su lugar.
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

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <Link
            href={`${base}/lotes`}
            className="rounded-2xl border border-lila/12 bg-superficie p-6 transition-colors hover:border-lila/45"
          >
            <span className="font-serif text-[26px] text-texto">Lotes</span>
            <p className="mt-2 text-[13px] leading-[1.55] text-texto-suave">
              Conjuntos cerrados de piezas, con su composición y su precio.
            </p>
          </Link>

          <Link
            href={`${base}/granel`}
            className="rounded-2xl border border-lila/12 bg-superficie p-6 transition-colors hover:border-lila/45"
          >
            <span className="font-serif text-[26px] text-texto">Granel</span>
            <p className="mt-2 text-[13px] leading-[1.55] text-texto-suave">
              Compra por gramo, con precio según la cantidad.
            </p>
          </Link>
        </div>
      </div>
    </main>
  );
}
