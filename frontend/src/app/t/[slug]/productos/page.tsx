import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Paginacion } from "@/components/tienda/paginacion";
import { TarjetaProducto } from "@/components/tienda/tarjeta-producto";
import { obtenerFormasDeVenta, obtenerProductos } from "@/lib/api/catalogo";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";
import { cn } from "@/lib/utils";

export const metadata: Metadata = { title: "Catálogo" };

function primero(valor: string | string[] | undefined): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

function numeroDePagina(valor: string | string[] | undefined): number {
  const numero = Number(primero(valor));
  return Number.isInteger(numero) && numero >= 1 ? numero : 1;
}

/**
 * El catálogo de la tienda.
 *
 * Las pestañas salen de lo que la tienda vende, no de una lista escrita acá:
 * una que solo venda por unidad no muestra ninguna, y otra que mañana agregue
 * venta por peso la muestra sin tocar este archivo.
 */
export default async function PaginaCatalogo({
  params,
  searchParams,
}: PageProps<"/t/[slug]/productos">) {
  const { slug } = await params;
  const { pagina, forma } = await searchParams;

  const tienda = await obtenerIdentidadTienda(slug);
  if (!tienda) {
    notFound();
  }

  const elegida = primero(forma);
  const [formas, catalogo] = await Promise.all([
    obtenerFormasDeVenta(slug),
    obtenerProductos(slug, { pagina: numeroDePagina(pagina), forma: elegida }),
  ]);

  const base = `/t/${slug}/productos`;

  return (
    <main className="mx-auto w-full max-w-[1280px] flex-1 px-5 py-10 lg:px-6">
      <h1 className="font-serif text-[38px] font-medium text-texto lg:text-[44px]">Catálogo</h1>

      {formas.length > 1 && (
        <nav aria-label="Formas de venta" className="mt-6 flex flex-wrap gap-2">
          <Pestana href={base} etiqueta="Todo" activa={!elegida} />
          {formas.map((f) => (
            <Pestana
              key={f.valor}
              href={`${base}?forma=${f.valor}`}
              etiqueta={f.nombre}
              activa={elegida === f.valor}
            />
          ))}
        </nav>
      )}

      {catalogo.productos.length === 0 ? (
        <p className="mt-10 text-sm text-texto-suave">
          Esta tienda todavía no tiene productos publicados.
        </p>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {catalogo.productos.map((producto) => (
            <TarjetaProducto key={producto.codigo} slugTienda={slug} producto={producto} />
          ))}
        </div>
      )}

      <div className="mt-10">
        <Paginacion
          base={elegida ? `${base}?forma=${elegida}` : base}
          paginaActual={catalogo.paginaActual}
          totalPaginas={catalogo.totalPaginas}
        />
      </div>
    </main>
  );
}

function Pestana({ href, etiqueta, activa }: { href: string; etiqueta: string; activa: boolean }) {
  return (
    <Link
      href={href}
      aria-current={activa ? "page" : undefined}
      className={cn(
        "rounded-full border px-4 py-2 text-[13px] transition-colors hover:no-underline",
        activa
          ? "border-lila/45 bg-violeta/20 font-semibold text-texto"
          : "border-lila/16 text-texto-suave hover:border-lila/40",
      )}
    >
      {etiqueta}
    </Link>
  );
}
