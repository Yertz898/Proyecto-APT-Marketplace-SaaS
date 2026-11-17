import type { Metadata } from "next";

import { ElegirContrasena } from "@/components/sesion/recuperar";

export const metadata: Metadata = { title: "Contraseña nueva" };

/** Adonde lleva el enlace del correo cuando se pidió desde esta tienda. */
export default async function PaginaRestablecer({ params, searchParams }: PageProps<"/t/[slug]/restablecer">) {
  const [{ slug }, consulta] = await Promise.all([params, searchParams]);
  const texto = (valor: string | string[] | undefined) => (typeof valor === "string" ? valor : "");

  return (
    <main className="mx-auto w-full max-w-[420px] flex-1 px-5 py-14">
      <ElegirContrasena
        uid={texto(consulta.uid)}
        token={texto(consulta.token)}
        hrefEntrar={`/t/${slug}/entrar`}
        hrefPedirOtro={`/t/${slug}/olvide-contrasena`}
      />
    </main>
  );
}
