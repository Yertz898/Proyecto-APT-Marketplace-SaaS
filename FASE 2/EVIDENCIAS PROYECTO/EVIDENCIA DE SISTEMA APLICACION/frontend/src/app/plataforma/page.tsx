import { PantallaPlataforma } from "@/components/plataforma/pantalla-plataforma";

/**
 * Portada de la administración de la plataforma: las tiendas, las solicitudes
 * de acceso y el registro de actividad.
 *
 * La pantalla es de cliente porque se dibuja con la sesión del navegador; la
 * ruta queda en servidor para que la pestaña tenga nombre.
 */
export const metadata = { title: "Administración" };

export default function PaginaDePlataforma() {
  return <PantallaPlataforma />;
}
