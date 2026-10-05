import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Catálogo" };

export default function PaginaCatalogo() {
  return (
    <>
      <Cabecera titulo="Catálogo" descripcion="Tus productos, su precio y su inventario." />
      <SinConectar seccion="El catálogo del panel" />
    </>
  );
}
