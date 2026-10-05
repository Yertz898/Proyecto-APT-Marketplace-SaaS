import { PantallaCatalogo } from "@/components/panel/pantalla-catalogo";

/*
 * La pantalla es de cliente porque se dibuja con la sesión del navegador, y un
 * componente de cliente no puede exportar metadata. Por eso la ruta se queda
 * acá, en servidor, y solo delega.
 */
export const metadata = { title: "Catálogo" };

export default function PaginaCatalogo() {
  return <PantallaCatalogo />;
}
