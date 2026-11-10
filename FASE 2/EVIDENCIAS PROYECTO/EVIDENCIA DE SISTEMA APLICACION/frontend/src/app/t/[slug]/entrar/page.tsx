import type { Metadata } from "next";

import { FormularioDeSesion } from "@/components/sesion/formulario";
import { rutaSegura, volverDe } from "@/lib/rutas";

export const metadata: Metadata = { title: "Iniciar sesión" };

/**
 * Inicio de sesión del comprador.
 *
 * Vive bajo /t/<slug> para conservar el aspecto de la tienda por la que llegó,
 * pero la cuenta es de la plataforma: la misma sirve en cualquier tienda.
 */
export default async function PaginaEntrar({ params, searchParams }: PageProps<"/t/[slug]/entrar">) {
  const [{ slug }, consulta] = await Promise.all([params, searchParams]);
  const base = `/t/${slug}`;

  return (
    <main className="mx-auto w-full max-w-[420px] flex-1 px-5 py-14">
      <FormularioDeSesion
        modo="entrar"
        destino={rutaSegura(volverDe(consulta), base)}
        hrefAlternativa={`${base}/crear-cuenta`}
        textoAlternativa="¿No tienes cuenta? Crear una"
      />
    </main>
  );
}
