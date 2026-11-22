import type { Metadata } from "next";

import { ResponderCambioPorEnlace } from "@/components/agenda/responder-por-enlace";
import { MarcoDeAcceso } from "@/components/sesion/marco-de-acceso";

export const metadata: Metadata = { title: "Cambio de hora" };

/**
 * Adonde lleva el enlace de Aceptar / Rechazar del correo de un cambio de hora.
 *
 * El enlace trae una firma que dice qué cambio es y quién responde, así que no
 * pide iniciar sesión. Igual muestra el cambio y pide confirmar con un botón:
 * los programas de correo abren los enlaces para revisarlos, y un enlace que
 * respondiera solo con abrirlo aceptaría cambios que nadie vio.
 */
export default async function PaginaCambioDeHora({ searchParams }: PageProps<"/agenda/cambio">) {
  const consulta = await searchParams;
  const firma = typeof consulta.firma === "string" ? consulta.firma : "";
  const respuesta = consulta.respuesta === "rechazar" ? "rechazar" : "aceptar";

  return (
    <MarcoDeAcceso>
      <ResponderCambioPorEnlace firma={firma} sugerida={respuesta} />
    </MarcoDeAcceso>
  );
}
