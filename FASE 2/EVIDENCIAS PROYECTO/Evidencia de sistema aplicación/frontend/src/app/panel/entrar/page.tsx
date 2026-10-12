import type { Metadata } from "next";

import { FormularioDeSesion } from "@/components/sesion/formulario";
import { rutaSegura, volverDe } from "@/lib/rutas";

export const metadata: Metadata = { title: "Iniciar sesión" };

/**
 * Entrada al panel de la tienda.
 *
 * No ofrece crear cuenta: las cuentas de dueño y de vendedor las crea la
 * tienda, no se registran solas.
 */
export default async function PaginaEntrarAlPanel({ searchParams }: PageProps<"/panel/entrar">) {
  const consulta = await searchParams;

  return (
    <main className="mx-auto w-full max-w-[420px] flex-1 px-5 py-14">
      <FormularioDeSesion
        modo="entrar"
        destino={rutaSegura(volverDe(consulta), "/panel")}
        hrefAlternativa={null}
      />
      <p className="mt-6 text-center text-[13px] text-texto-suave">
        Las cuentas del panel las crea la tienda. Si no tienes uno, pídeselo al dueño.
      </p>
    </main>
  );
}
