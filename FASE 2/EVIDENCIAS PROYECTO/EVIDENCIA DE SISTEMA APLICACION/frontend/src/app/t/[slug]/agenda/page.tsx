import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { CalendarioDeVisitas } from "@/components/tienda/calendario-visitas";
import { obtenerAgenda } from "@/lib/api/agenda";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Agendar visita" };

const FECHA = /^\d{4}-\d{2}-\d{2}$/;

/** Lo más que el backend entrega en una consulta: un mes de horas. */
const DIAS_POR_CONSULTA = 31;

/**
 * Agenda de visitas a la oficina de la tienda, como calendario.
 *
 * Trae un mes de horas a partir del día pedido. El día va en la dirección
 * (`?dia=aaaa-mm-dd`) y no solo en el estado del componente, así se puede
 * compartir una fecha concreta y volver atrás sin perderla.
 */
export default async function PaginaAgenda({ params, searchParams }: PageProps<"/t/[slug]/agenda">) {
  const [{ slug }, consulta] = await Promise.all([params, searchParams]);

  // Una fecha mal escrita en la dirección no es un error del comprador que
  // valga un 404: se ignora y se parte desde el primer día disponible.
  const dia = typeof consulta.dia === "string" && FECHA.test(consulta.dia) ? consulta.dia : undefined;

  const [tienda, agenda] = await Promise.all([
    obtenerIdentidadTienda(slug),
    obtenerAgenda(slug, { desde: dia, dias: DIAS_POR_CONSULTA }),
  ]);

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
        {agenda.anticipacionMinimaHoras} horas de anticipación, y la tienda confirma cada visita.
      </p>

      <div className="mt-8">
        {/* La llave reinicia el calendario cuando llega otro mes de horas. */}
        <CalendarioDeVisitas key={`${agenda.rango.desde}-${dia ?? ""}`} slug={slug} agenda={agenda} diaPedido={dia} />
      </div>
    </main>
  );
}
