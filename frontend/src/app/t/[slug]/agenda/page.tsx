import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { SelectorDeHoras } from "@/components/tienda/selector-horas";
import { obtenerAgenda } from "@/lib/api/agenda";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Agendar visita" };

/** Agenda de visitas a la oficina de la tienda. */
export default async function PaginaAgenda({ params }: PageProps<"/t/[slug]/agenda">) {
  const { slug } = await params;
  const [tienda, agenda] = await Promise.all([obtenerIdentidadTienda(slug), obtenerAgenda(slug)]);

  if (!tienda) {
    notFound();
  }

  // Una tienda puede no recibir visitas con hora: en ese caso no hay agenda.
  if (!agenda) {
    notFound();
  }

  return (
    <main className="mx-auto w-full max-w-[1100px] flex-1 px-5 py-10 lg:px-6">
      <h1 className="font-serif text-[38px] font-medium text-texto lg:text-[44px]">Agendar visita</h1>

      {agenda.direccion && <p className="mt-2 text-sm text-texto-suave">{agenda.direccion}</p>}
      {agenda.indicaciones && (
        <p className="mt-1 text-[13px] leading-[1.6] text-texto-suave">{agenda.indicaciones}</p>
      )}

      <p className="mt-4 text-[13px] text-texto-suave">
        Las horas se muestran en hora de Chile. Se puede reservar con al menos{" "}
        {agenda.anticipacionMinimaHoras} horas de anticipación.
      </p>

      <div className="mt-8">
        <SelectorDeHoras horas={agenda.horas} />
      </div>
    </main>
  );
}
