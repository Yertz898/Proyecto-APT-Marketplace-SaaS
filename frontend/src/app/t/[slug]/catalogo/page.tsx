import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { FiltrosEscritorio, FiltrosMovil } from "@/components/tienda/filtros-catalogo";
import { IconoFlechaAbajo } from "@/components/tienda/iconos";
import { Paginacion } from "@/components/tienda/paginacion";
import { TarjetaProducto } from "@/components/tienda/tarjeta-producto";
import { obtenerCatalogo } from "@/lib/api/catalogo";
import { obtenerTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Catálogo" };

function numeroDePagina(valor: string | string[] | undefined): number {
  const numero = Number(Array.isArray(valor) ? valor[0] : valor);
  return Number.isInteger(numero) && numero >= 1 ? numero : 1;
}

/** Catálogo completo (mockup 1B). */
export default async function PaginaCatalogo({ params, searchParams }: PageProps<"/t/[slug]/catalogo">) {
  const { slug } = await params;
  const { pagina } = await searchParams;

  const tienda = await obtenerTienda(slug);
  if (!tienda) {
    notFound();
  }

  const catalogo = await obtenerCatalogo(slug, numeroDePagina(pagina));
  const base = `/t/${slug}`;

  return (
    <main className="flex-1">
      <div className="mx-auto max-w-[1280px] px-5 pt-[26px] lg:px-6 lg:pt-[38px]">
        <nav aria-label="Ubicación" className="text-xs text-texto-suave">
          <Link href={base} className="transition-colors hover:text-texto">
            Inicio
          </Link>
          {" · "}
          <span className="text-texto">Catálogo</span>
        </nav>

        <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-serif text-[38px] font-medium text-texto lg:text-[44px]">Catálogo completo</h1>
            <p className="mt-1.5 text-[13px] text-texto-suave">
              {catalogo.total} piezas · {catalogo.totalConMayorista} con precio mayorista activo
            </p>
          </div>

          <div className="flex items-center gap-3">
            <FiltrosMovil filtros={catalogo.filtros} />
            <span className="hidden text-[13px] text-texto-suave sm:inline">Ordenar por</span>
            <div
              data-pendiente="orden"
              className="flex h-[42px] items-center gap-2.5 rounded-[10px] border border-lila/20 bg-superficie px-4 text-[13px] text-texto"
            >
              Más vendidos
              <IconoFlechaAbajo />
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto grid max-w-[1280px] items-start gap-9 px-5 pt-[30px] pb-[70px] lg:grid-cols-[264px_minmax(0,1fr)] lg:px-6">
        <FiltrosEscritorio filtros={catalogo.filtros} />

        <div className="grid grid-cols-2 gap-3.5 md:grid-cols-3 lg:gap-[22px]">
          {catalogo.productos.map((producto) => (
            <TarjetaProducto key={producto.slug} slugTienda={slug} producto={producto} altura="catalogo" />
          ))}
        </div>
      </div>

      <div className="mx-auto max-w-[1280px] px-5 lg:px-6">
        <Paginacion
          base={`${base}/catalogo`}
          paginaActual={catalogo.paginaActual}
          totalPaginas={catalogo.totalPaginas}
        />
      </div>
    </main>
  );
}
