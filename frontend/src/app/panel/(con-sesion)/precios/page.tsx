import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Precios" };

export default function PaginaPrecios() {
  return (
    <>
      <Cabecera titulo="Precios" descripcion="Los tramos por cantidad de cada línea de granel." />
      <SinConectar seccion="El editor de tramos" />
    </>
  );
}
