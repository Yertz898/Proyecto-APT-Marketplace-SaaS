import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { MisCitas } from "@/components/tienda/mis-citas";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Mis citas" };

/**
 * Las visitas que el comprador agendó en esta tienda.
 *
 * La lista se pide desde el navegador, con la sesión del comprador: el
 * servidor de Next no tiene su token.
 */
export default async function PaginaMisCitas({ params }: PageProps<"/t/[slug]/cuenta/citas">) {
  const { slug } = await params;
  const tienda = await obtenerIdentidadTienda(slug);
  if (!tienda) notFound();

  return (
    <main className="mx-auto w-full max-w-[860px] flex-1 px-5 py-10 lg:px-6">
      <h1 className="font-serif text-[38px] font-medium text-texto lg:text-[44px]">Mis citas</h1>
      <p className="mt-2 text-sm text-texto-suave">
        Tus visitas a {tienda.nombre}. Puedes reagendarlas o cancelarlas; las horas están en hora de Chile.
      </p>
      <div className="mt-8">
        <MisCitas slug={slug} />
      </div>
    </main>
  );
}
