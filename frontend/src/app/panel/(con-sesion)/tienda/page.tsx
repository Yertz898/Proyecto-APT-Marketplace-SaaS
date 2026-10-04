import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Tienda y marca" };

export default function PaginaTienda() {
  return (
    <>
      <Cabecera titulo="Tienda y marca" descripcion="Tu logo, tus colores y tu tipografía." />
      <SinConectar seccion="El perfil de la tienda" />
    </>
  );
}
