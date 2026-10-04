import { PantallaPlan } from "@/components/panel/pantalla-plan";

/*
 * La pantalla es de cliente porque se dibuja con la sesión del navegador, y un
 * componente de cliente no puede exportar metadata. Por eso la ruta se queda
 * acá, en servidor, y solo delega: así la pestaña tiene nombre.
 */
export const metadata = { title: "Plan" };

export default function PaginaPlan() {
  return <PantallaPlan />;
}
