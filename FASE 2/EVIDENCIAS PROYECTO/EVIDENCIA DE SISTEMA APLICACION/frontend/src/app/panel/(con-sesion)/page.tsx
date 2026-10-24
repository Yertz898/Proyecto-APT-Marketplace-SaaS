import { PantallaInicio } from "@/components/panel/pantalla-inicio";

/*
 * La pantalla es de cliente porque se dibuja con la sesión del navegador, y un
 * componente de cliente no puede exportar metadata. Por eso la ruta se queda
 * acá, en servidor, y solo delega: así la pestaña tiene nombre.
 */
export const metadata = { title: "Inicio" };

export default function PaginaInicio() {
  return <PantallaInicio />;
}
