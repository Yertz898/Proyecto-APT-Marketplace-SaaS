import type { AgendaPublica } from "@/lib/tipos";

import { API_SERVIDOR as API } from "./base";

/*
 * Agenda de visitas de la tienda pública.
 *
 * Las horas disponibles las calcula el backend con la configuración de la
 * tienda: horarios, días bloqueados, anticipación, ventana y cupos. El
 * navegador solo las muestra.
 *
 * Se piden de a pocos días. La ventana de una tienda puede ser de un mes, y
 * traerse el mes entero son cientos de horas para una sola pantalla.
 */

/** Días que trae cada pantalla de la agenda. */
export const DIAS_POR_PANTALLA = 7;

export async function obtenerAgenda(
  slug: string,
  rango?: { desde?: string; dias?: number },
): Promise<AgendaPublica | null> {
  const parametros = new URLSearchParams();
  if (rango?.desde) parametros.set("desde", rango.desde);
  if (rango?.dias) parametros.set("dias", String(rango.dias));

  const consulta = parametros.size > 0 ? `?${parametros}` : "";

  try {
    const respuesta = await fetch(`${API}/t/${encodeURIComponent(slug)}/agenda/horas${consulta}`, {
      // Los cupos cambian cuando alguien reserva: no conviene cachearlos.
      cache: "no-store",
    });

    if (!respuesta.ok) {
      return null;
    }

    return (await respuesta.json()) as AgendaPublica;
  } catch {
    return null;
  }
}
