import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Catálogo" };

export default function PaginaCatalogo() {
  return (
    <>
      <Cabecera titulo="Catálogo" descripcion="Tus lotes y tus líneas de granel." />
      <SinConectar seccion="El catálogo del panel" />
    </>
  );
}
