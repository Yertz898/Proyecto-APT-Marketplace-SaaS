import type { Metadata } from "next";

import { NavegacionPanel } from "@/components/panel/navegacion";

export const metadata: Metadata = {
  title: { default: "Panel", template: "%s · Panel" },
};

/*
 * Marco del panel de la tienda.
 *
 * Es una aplicación distinta de la tienda pública: no comparte componentes con
 * ella y nunca se sirve bajo /t/<slug>. La tienda del usuario sale de su sesión,
 * no de la URL.
 *
 * PENDIENTE DE SEGURIDAD: el panel todavía no exige autenticación, por decisión
 * de equipo para poder construirlo sin backend. No debe desplegarse así al
 * ambiente de pruebas: la carga masiva escribe el catálogo de la tienda.
 */
export default function LayoutPanel({ children }: LayoutProps<"/panel">) {
  return (
    <div className="flex min-h-full flex-1 flex-col">
      <NavegacionPanel />
      <main className="mx-auto w-full max-w-[1100px] flex-1 px-5 py-8 lg:px-8 lg:py-10">{children}</main>
    </div>
  );
}
