import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { NavegacionSemana } from "@/components/tienda/navegacion-semana";
import { SelectorDeHoras } from "@/components/tienda/selector-horas";
import { DIAS_POR_PANTALLA, obtenerAgenda } from "@/lib/api/agenda";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Agendar visita" };

const FECHA = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Agenda de visitas a la oficina de la tienda.
 *
 * Se muestra una semana a la vez. La ventana de una tienda puede ser de un mes
 * entero, y ofrecer las cientos de horas de un mes en una sola pantalla no es
 * una lista: es un muro.
 *
 * La semana va en la dirección y no en el estado del componente, así se puede
 * compartir un día concreto y volver atrás sin perderlo.
 */
export default async function PaginaAgenda({ params, searchParams }: PageProps<"/t/[slug]/agenda">) {
  const [{ slug }, consulta] = await Promise.all([params, searchParams]);

  // Una fecha mal escrita en la dirección no es un error del comprador que
  // valga un 404: se ignora y se parte desde el primer día disponible.
  const pedida = typeof consulta.desde === "string" && FECHA.test(consulta.desde) ? consulta.desde : undefined;

  const [tienda, agenda] = await Promise.all([
    obtenerIdentidadTienda(slug),
    obtenerAgenda(slug, { desde: pedida, dias: DIAS_POR_PANTALLA }),
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
        {agenda.anticipacionMinimaHoras} horas de anticipación.
      </p>

      <div className="mt-8 border-y border-lila/12 py-3">
        <NavegacionSemana
          base={`/t/${slug}/agenda`}
          rango={agenda.rango}
          ventana={agenda.ventana}
          dias={DIAS_POR_PANTALLA}
        />
      </div>

      <div className="mt-8">
        <SelectorDeHoras horas={agenda.horas} />
      </div>
    </main>
  );
}
