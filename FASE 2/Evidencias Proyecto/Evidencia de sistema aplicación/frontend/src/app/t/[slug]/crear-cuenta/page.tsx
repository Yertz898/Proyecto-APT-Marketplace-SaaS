import type { Metadata } from "next";

import { FormularioDeSesion } from "@/components/sesion/formulario";
import { rutaSegura, volverDe } from "@/lib/rutas";

export const metadata: Metadata = { title: "Crear cuenta" };

/**
 * Alta de un comprador.
 *
 * Es la única cuenta que se crea sola. Las de dueño y vendedor las crea la
 * tienda, y la de administrador no se crea desde la interfaz.
 */
export default async function PaginaCrearCuenta({
  params,
  searchParams,
}: PageProps<"/t/[slug]/crear-cuenta">) {
  const [{ slug }, consulta] = await Promise.all([params, searchParams]);
  const base = `/t/${slug}`;

  return (
    <main className="mx-auto w-full max-w-[420px] flex-1 px-5 py-14">
      <FormularioDeSesion
        modo="crear-cuenta"
        destino={rutaSegura(volverDe(consulta), base)}
        hrefAlternativa={`${base}/entrar`}
        textoAlternativa="¿Ya tienes cuenta? Iniciar sesión"
      />
    </main>
  );
}
