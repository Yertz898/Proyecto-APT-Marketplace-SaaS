import type { AgendaPublica } from "@/lib/tipos";

/*
 * Agenda de visitas de la tienda pública.
 *
 * Las horas disponibles las calcula el backend con la configuración de la
 * tienda: horarios, días bloqueados, anticipación, ventana y cupos. El
 * navegador solo las muestra.
 */

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export async function obtenerAgenda(
  slug: string,
  rango?: { desde?: string; hasta?: string },
): Promise<AgendaPublica | null> {
  const parametros = new URLSearchParams();
  if (rango?.desde) parametros.set("desde", rango.desde);
  if (rango?.hasta) parametros.set("hasta", rango.hasta);

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
