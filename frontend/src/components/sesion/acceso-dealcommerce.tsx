"use client";

import { FormularioDeSesion } from "@/components/sesion/formulario";
import { esAdminDePlataforma } from "@/components/sesion/usar-sesion";
import { rutaSegura } from "@/lib/rutas";

/*
 * El formulario del acceso a DealCommerce.
 *
 * Está separado de la página porque el destino depende del rol, y eso es una
 * función: no cruza la frontera del servidor. La página se queda siendo de
 * servidor y conserva su metadata.
 */
export function AccesoDealCommerce({ volver }: { volver?: string }) {
  return (
    <FormularioDeSesion
      modo="entrar"
      tema="claro"
      // Quien administra la plataforma no tiene tienda, así que el panel de una
      // tienda no le sirve de nada.
      destino={(sesion) => rutaSegura(volver, esAdminDePlataforma(sesion) ? "/plataforma" : "/panel")}
      hrefAlternativa={null}
    />
  );
}
