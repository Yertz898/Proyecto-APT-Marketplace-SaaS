import type { Metadata } from "next";

export const metadata: Metadata = {
  title: { default: "Panel", template: "%s · Panel" },
};

/*
 * Marco del panel de la tienda.
 *
 * Es una aplicación distinta de la tienda pública: no comparte componentes con
 * ella y nunca se sirve bajo /t/<slug>. La tienda del usuario sale de su
 * sesión, no de la URL.
 *
 * Acá no hay guardia ni barra: el formulario de entrada también vive bajo
 * /panel y no puede quedar detrás de la puerta que lleva hasta él. Todo lo que
 * sí exige sesión está en el grupo (con-sesion).
 */
export default function LayoutPanel({ children }: LayoutProps<"/panel">) {
  return <div className="flex min-h-full flex-1 flex-col">{children}</div>;
}
