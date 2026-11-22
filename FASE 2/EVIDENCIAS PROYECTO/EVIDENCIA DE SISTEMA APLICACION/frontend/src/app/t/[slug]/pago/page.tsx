import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ResultadoDelPago } from "@/components/tienda/resultado-pago";
import { obtenerIdentidadTienda } from "@/lib/api/tienda";

export const metadata: Metadata = { title: "Pago" };

/**
 * Adonde vuelve el cliente después de Webpay.
 *
 * El backend ya le preguntó a Transbank cómo terminó el pago y dejó el pedido
 * confirmado o anulado; acá solo se muestra. El estado viene en la dirección
 * y sirve para elegir el mensaje: no decide nada, así que cambiarlo a mano no
 * paga ningún pedido.
 */
export default async function PaginaPago({ params, searchParams }: PageProps<"/t/[slug]/pago">) {
  const [{ slug }, consulta] = await Promise.all([params, searchParams]);
  const tienda = await obtenerIdentidadTienda(slug);
  if (!tienda) notFound();

  const folio = typeof consulta.folio === "string" ? consulta.folio : "";
  const estado = typeof consulta.estado === "string" ? consulta.estado : "";

  return (
    <main className="mx-auto w-full max-w-[640px] flex-1 px-5 py-14 lg:px-6">
      <ResultadoDelPago slug={slug} folio={folio} estado={estado} whatsapp={tienda.redes.whatsapp} />
    </main>
  );
}
