import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";

import { Carrusel, Diapositiva } from "@/components/tienda/carrusel";
import { TarjetaProducto } from "@/components/tienda/tarjeta-producto";
import { obtenerDestacados, obtenerFormasDeVenta } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";
import type { FormaDeVenta, IdentidadTienda, Producto } from "@/lib/tipos";

/**
 * Portada de la tienda pública.
 *
 * Tiene una presentación, los carruseles con lo más vendido y lo nuevo, y
 * accesos por forma de venta. Cómo se ordena todo eso lo decide la plantilla
 * que eligió la tienda; el contenido es siempre el mismo.
 *
 * Nada se inventa: sin ventas no hay carrusel de más vendidos, y sin banner
 * la portada se arma con el nombre y los colores de la tienda.
 */
export default async function InicioTienda({ params }: PageProps<"/t/[slug]">) {
  const { slug } = await params;
  const [tienda, destacados, formas] = await Promise.all([
    obtenerIdentidadTienda(slug),
    obtenerDestacados(slug),
    obtenerFormasDeVenta(slug),
  ]);

  if (!tienda) {
    notFound();
  }

  const base = `/t/${slug}`;
  const plantilla = tienda.plantilla ?? "clasica";

  const masVendidos = destacados.masVendidos.length > 0 && (
    <FilaDeProductos titulo="Lo más vendido" productos={destacados.masVendidos} base={base} slug={slug} />
  );
  const nuevos = destacados.nuevos.length > 0 && (
    <FilaDeProductos titulo="Recién llegados" productos={destacados.nuevos} base={base} slug={slug} />
  );

  return (
    <main className="flex flex-1 flex-col gap-14 pb-16 lg:gap-20">
      {plantilla === "moderna" ? (
        <PortadaModerna tienda={tienda} base={base} />
      ) : plantilla === "minimal" ? (
        <PortadaMinimal tienda={tienda} base={base} />
      ) : (
        <PortadaClasica tienda={tienda} base={base} />
      )}

      {plantilla === "moderna" && destacados.masVendidos.length > 0 ? (
        <GrillaDestacada productos={destacados.masVendidos} base={base} slug={slug} />
      ) : (
        masVendidos
      )}

      {formas.length > 1 && <ComoVendemos formas={formas} base={base} />}

      {nuevos}

      <Contacto tienda={tienda} base={base} />
    </main>
  );
}

// ── Portadas ────────────────────────────────────────────────────────────────

function BotonCatalogo({ base, children = "Ver el catálogo" }: { base: string; children?: ReactNode }) {
  return (
    <Link
      href={`${base}/productos`}
      className="inline-flex h-12 items-center rounded-full bg-violeta px-7 text-sm font-semibold text-white transition-colors hover:bg-violeta-hover hover:no-underline"
    >
      {children}
    </Link>
  );
}

function PortadaClasica({ tienda, base }: { tienda: IdentidadTienda; base: string }) {
  return (
    <section className="relative isolate flex min-h-[340px] items-end overflow-hidden lg:min-h-[520px]">
      {tienda.banner ? (
        <>
          <Image src={tienda.banner.url} alt={tienda.banner.alt} fill priority sizes="100vw" className="-z-10 object-cover" />
          <div className="absolute inset-0 -z-10 bg-gradient-to-t from-black/75 via-black/30 to-transparent" />
        </>
      ) : (
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-violeta/45 via-tinta to-tinta" />
      )}
      <div className="mx-auto w-full max-w-[1280px] px-5 pt-24 pb-12 lg:px-6 lg:pb-16">
        <p className="text-[13px] font-semibold tracking-[0.18em] text-white/80 uppercase">Bienvenida</p>
        <h1 className="mt-2 max-w-[760px] font-serif text-[44px] leading-[1.05] font-medium text-white lg:text-[72px]">
          {tienda.nombre}
        </h1>
        <div className="mt-7">
          <BotonCatalogo base={base} />
        </div>
      </div>
    </section>
  );
}

function PortadaModerna({ tienda, base }: { tienda: IdentidadTienda; base: string }) {
  return (
    <section className="mx-auto grid w-full max-w-[1280px] items-center gap-8 px-5 pt-10 lg:grid-cols-2 lg:px-6 lg:pt-14">
      <div>
        <span className="inline-flex rounded-full bg-violeta/15 px-3 py-1 text-[12px] font-semibold text-lila">
          Compra directo a la tienda
        </span>
        <h1 className="mt-4 font-serif text-[44px] leading-[1.02] text-texto lg:text-[64px]">{tienda.nombre}</h1>
        <p className="mt-4 max-w-[460px] text-[16px] leading-[1.6] text-texto-suave">
          Precios que bajan mientras más llevas. Arma tu pedido y lo coordinamos contigo por WhatsApp.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <BotonCatalogo base={base}>Comprar ahora</BotonCatalogo>
        </div>
      </div>
      <div className="relative aspect-[4/3] overflow-hidden rounded-[18px] bg-gradient-to-br from-violeta/50 to-lila/20">
        {tienda.banner && (
          <Image src={tienda.banner.url} alt={tienda.banner.alt} fill priority sizes="(min-width: 1024px) 640px, 100vw" className="object-cover" />
        )}
      </div>
    </section>
  );
}

function PortadaMinimal({ tienda, base }: { tienda: IdentidadTienda; base: string }) {
  return (
    <section className="mx-auto w-full max-w-[1100px] px-5 pt-16 text-center lg:pt-24">
      <h1 className="font-serif text-[40px] leading-[1.1] text-texto lg:text-[60px]">{tienda.nombre}</h1>
      <div className="mt-7">
        <BotonCatalogo base={base} />
      </div>
      {tienda.banner && (
        <div className="relative mt-12 aspect-[21/9] overflow-hidden rounded-[18px]">
          <Image src={tienda.banner.url} alt={tienda.banner.alt} fill priority sizes="(min-width: 1100px) 1100px, 100vw" className="object-cover" />
        </div>
      )}
    </section>
  );
}

// ── Secciones ───────────────────────────────────────────────────────────────

function FilaDeProductos({
  titulo,
  productos,
  base,
  slug,
}: {
  titulo: string;
  productos: Producto[];
  base: string;
  slug: string;
}) {
  return (
    <Carrusel
      titulo={titulo}
      accion={
        <Link href={`${base}/productos`} className="mr-2 text-[14px] font-semibold text-lila">
          Ver todo
        </Link>
      }
    >
      {productos.map((producto) => (
        <Diapositiva key={producto.codigo}>
          <TarjetaProducto slugTienda={slug} producto={producto} />
        </Diapositiva>
      ))}
    </Carrusel>
  );
}

/** La plantilla moderna muestra sus más vendidos en grilla, con el primero destacado. */
function GrillaDestacada({ productos, base, slug }: { productos: Producto[]; base: string; slug: string }) {
  return (
    <section className="mx-auto w-full max-w-[1280px] px-5 lg:px-6">
      <div className="mb-5 flex items-end justify-between">
        <h2 className="font-serif text-[28px] text-texto lg:text-[34px]">Lo más vendido</h2>
        <Link href={`${base}/productos`} className="text-[14px] font-semibold text-lila">
          Ver todo
        </Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {productos.slice(0, 8).map((producto) => (
          <TarjetaProducto key={producto.codigo} slugTienda={slug} producto={producto} />
        ))}
      </div>
    </section>
  );
}

const DESCRIPCION_DE_FORMA: Record<string, string> = {
  unidad: "Elige pieza por pieza.",
  lote: "Paquetes armados, ideales para revender.",
  peso: "Pide los gramos que necesites.",
};

function ComoVendemos({ formas, base }: { formas: FormaDeVenta[]; base: string }) {
  return (
    <section className="mx-auto w-full max-w-[1280px] px-5 lg:px-6">
      <h2 className="mb-5 font-serif text-[28px] text-texto lg:text-[34px]">Cómo quieres comprar</h2>
      <div className="grid gap-4 sm:grid-cols-3">
        {formas.map((forma) => (
          <Link
            key={forma.valor}
            href={`${base}/productos?forma=${forma.valor}`}
            className="group rounded-[18px] border border-lila/12 bg-superficie p-6 transition-colors hover:border-lila/45 hover:no-underline"
          >
            <span className="block font-serif text-[22px] text-texto">{forma.nombre}</span>
            <span className="mt-1 block text-[14px] text-texto-suave">{DESCRIPCION_DE_FORMA[forma.valor] ?? ""}</span>
            <span className="mt-4 inline-block text-[13px] font-semibold text-lila group-hover:underline">Ver productos →</span>
          </Link>
        ))}
      </div>
    </section>
  );
}

function Contacto({ tienda, base }: { tienda: IdentidadTienda; base: string }) {
  if (!tienda.redes.whatsapp && !tienda.redes.instagram) {
    return null;
  }
  return (
    <section className="mx-auto w-full max-w-[1280px] px-5 lg:px-6">
      <div className="flex flex-col items-start justify-between gap-5 rounded-[18px] bg-violeta/12 p-8 lg:flex-row lg:items-center lg:p-10">
        <div>
          <p className="font-serif text-[26px] text-texto">¿Tienes dudas antes de comprar?</p>
          <p className="mt-1 text-[15px] text-texto-suave">Escríbenos y te ayudamos a armar tu pedido.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {tienda.redes.whatsapp && (
            <a
              href={tienda.redes.whatsapp}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-12 items-center rounded-full bg-violeta px-6 text-sm font-semibold text-white hover:bg-violeta-hover hover:no-underline"
            >
              Escribir por WhatsApp
            </a>
          )}
          {tienda.redes.instagram && (
            <a
              href={tienda.redes.instagram}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-12 items-center rounded-full border border-lila/40 px-6 text-sm font-semibold text-texto hover:bg-violeta/15 hover:no-underline"
            >
              Ver Instagram
            </a>
          )}
          <Link
            href={`${base}/productos`}
            className="inline-flex h-12 items-center rounded-full border border-lila/40 px-6 text-sm font-semibold text-texto hover:bg-violeta/15 hover:no-underline"
          >
            Ir al catálogo
          </Link>
        </div>
      </div>
    </section>
  );
}
