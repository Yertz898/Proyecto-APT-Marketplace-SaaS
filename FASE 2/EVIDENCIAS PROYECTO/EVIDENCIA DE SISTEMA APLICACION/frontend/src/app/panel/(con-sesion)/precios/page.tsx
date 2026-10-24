import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Precios" };

export default function PaginaPrecios() {
  return (
    <>
      <Cabecera titulo="Precios" descripcion="Los tramos de precio por volumen de cada producto." />
      <SinConectar seccion="El editor de tramos" />
    </>
  );
}
