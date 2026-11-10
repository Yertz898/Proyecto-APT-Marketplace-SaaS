import type { Metadata } from "next";
import Link from "next/link";

import { Marca } from "@/components/portada/marca";
import { AccesoDealCommerce } from "@/components/sesion/acceso-dealcommerce";
import { volverDe } from "@/lib/rutas";

export const metadata: Metadata = { title: "Entrar a DealCommerce" };

/**
 * Acceso a DealCommerce.
 *
 * Es el de la plataforma, no el de una tienda: entran por acá el administrador
 * y quienes trabajan en una tienda suscrita. Por eso lleva la marca de
 * DealCommerce y su paleta clara, y no la de ninguna tienda en particular.
 *
 * No ofrece crear cuenta: las cuentas de dueño y de vendedor las crea la
 * plataforma, no se registran solas.
 */
export default async function PaginaEntrarADealCommerce({ searchParams }: PageProps<"/panel/entrar">) {
  const consulta = await searchParams;

  return (
    <div
      data-tema="claro"
      className="@container flex min-h-dvh w-full flex-col bg-hueso font-inter text-marino"
    >
      <header className="border-b border-arena">
        <div className="mx-auto flex max-w-[1280px] items-center px-[clamp(20px,5.5cqi,80px)] py-[14px]">
          <Link href="/" className="flex items-center gap-2.5 text-marino no-underline hover:no-underline">
            <Marca />
          </Link>
        </div>
      </header>

      <main className="mx-auto w-full max-w-[420px] flex-1 px-5 py-14">
        <AccesoDealCommerce volver={volverDe(consulta)} />

        <p className="mt-6 text-center text-[13px] text-pizarra">
          Las cuentas las crea la plataforma. Si trabajas en una tienda y no tienes acceso, pídeselo
          al dueño.
        </p>
      </main>
    </div>
  );
}
