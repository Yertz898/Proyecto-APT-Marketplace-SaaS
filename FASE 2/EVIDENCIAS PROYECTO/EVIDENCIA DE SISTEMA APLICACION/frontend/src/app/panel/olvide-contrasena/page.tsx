import type { Metadata } from "next";

import { PedirEnlace } from "@/components/sesion/recuperar";

import { MarcoDeAcceso } from "@/components/sesion/marco-de-acceso";

export const metadata: Metadata = { title: "Recuperar contraseña" };

/** «¿Olvidaste tu contraseña?» de quien trabaja en una tienda o administra la plataforma. */
export default function PaginaOlvideContrasenaPanel() {
  return (
    <MarcoDeAcceso>
      <PedirEnlace tema="claro" hrefEntrar="/panel/entrar" />
    </MarcoDeAcceso>
  );
}
