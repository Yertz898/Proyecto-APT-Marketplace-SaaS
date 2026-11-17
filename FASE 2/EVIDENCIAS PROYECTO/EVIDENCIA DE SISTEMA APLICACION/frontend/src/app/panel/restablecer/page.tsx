import type { Metadata } from "next";

import { ElegirContrasena } from "@/components/sesion/recuperar";

import { MarcoDeAcceso } from "@/components/sesion/marco-de-acceso";

export const metadata: Metadata = { title: "Contraseña nueva" };

/** Adonde lleva el enlace del correo pedido desde el acceso de DealCommerce. */
export default async function PaginaRestablecerPanel({ searchParams }: PageProps<"/panel/restablecer">) {
  const consulta = await searchParams;
  const texto = (valor: string | string[] | undefined) => (typeof valor === "string" ? valor : "");

  return (
    <MarcoDeAcceso>
      <ElegirContrasena
        tema="claro"
        uid={texto(consulta.uid)}
        token={texto(consulta.token)}
        hrefEntrar="/panel/entrar"
        hrefPedirOtro="/panel/olvide-contrasena"
      />
    </MarcoDeAcceso>
  );
}
