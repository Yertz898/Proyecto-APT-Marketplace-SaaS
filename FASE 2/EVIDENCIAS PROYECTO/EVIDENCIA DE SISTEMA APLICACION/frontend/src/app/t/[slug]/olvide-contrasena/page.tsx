import type { Metadata } from "next";

import { PedirEnlace } from "@/components/sesion/recuperar";

export const metadata: Metadata = { title: "Recuperar contraseña" };

/** «¿Olvidaste tu contraseña?» del comprador, con el aspecto de la tienda. */
export default async function PaginaOlvideContrasena({ params }: PageProps<"/t/[slug]/olvide-contrasena">) {
  const { slug } = await params;

  return (
    <main className="mx-auto w-full max-w-[420px] flex-1 px-5 py-14">
      <PedirEnlace tienda={slug} hrefEntrar={`/t/${slug}/entrar`} />
    </main>
  );
}
