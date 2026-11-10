import { Cabecera, SinConectar } from "@/components/panel/piezas";

export const metadata = { title: "Panel de ventas" };

export default function PaginaVentas() {
  return (
    <>
      <Cabecera titulo="Panel de ventas" descripcion="Cómo va el mes comparado con el anterior." />
      <SinConectar seccion="El panel de ventas" />
    </>
  );
}
